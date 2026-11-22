#!/usr/bin/env bash
#
# One-shot release: build + push the amd64 API image, publish the static frontend, redeploy on the VPS.
#
# The manual process this replaces is four order-sensitive steps across two machines, and it fails
# quietly in three specific ways — all now handled here:
#   1. building for the wrong CPU  → the host gets an image it cannot run (`exec format error`)
#   2. `docker compose up -d` without `pull` → the stale cached image keeps running, "deploy" does nothing
#   3. the container crash-looping → `up -d` still exits 0, so a broken release looks successful
#
# Usage:
#   cp .deploy.env.example .deploy.env   # once, then fill in WEB_ROOT / COMPOSE_DIR
#   ./scripts/release.sh                 # real release
#   ./scripts/release.sh --dry-run       # print every command, touch nothing
#   ./scripts/release.sh --skip-checks   # you already ran pytest/build by hand
#
set -euo pipefail

# ---------------------------------------------------------------- config (env or .deploy.env)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -f .deploy.env ]]; then
  # shellcheck disable=SC1091
  source .deploy.env
fi

HOST="${HOST:-do}"                                            # ssh alias
IMAGE="${IMAGE:-deejtsn/private:chores_api_v1}"               # Docker Hub repo (no tag)
PLATFORM="${PLATFORM:-linux/amd64}"                           # VPS arch; the dev Mac is arm64
API_BASE="${API_BASE:-https://chores.dempseypalaciotascon.com/api}"
WEB_ROOT="${WEB_ROOT:-}"                                      # required: nginx web root on the host
COMPOSE_DIR="${COMPOSE_DIR:-}"                                # required: compose file dir on the host
REMOTE_DB="${REMOTE_DB:-$COMPOSE_DIR/BE/data/database.db}"     # SQLite file backing the volume

DRY_RUN=0
SKIP_CHECKS=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --skip-checks) SKIP_CHECKS=1 ;;
    -h|--help) awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown argument: $arg (try --help)" >&2; exit 2 ;;
  esac
done

# ---------------------------------------------------------------- helpers
step()  { printf '\n\033[1m▸ %s\033[0m\n' "$*"; }
ok()    { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn()  { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()   { printf '\n\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
run()   { printf '  $ %s\n' "$*"; [ "$DRY_RUN" -eq 1 ] || eval "$@"; }
# Run a command on the host. Quoted for a plain (non-quoted) ssh invocation.
remote() { printf '  $ ssh %s %s\n' "$HOST" "$1"; [ "$DRY_RUN" -eq 1 ] || ssh "$HOST" "$1"; }

# ---------------------------------------------------------------- preflight
step "Preflight"
[[ -n "$WEB_ROOT" ]]    || die "WEB_ROOT is not set (copy .deploy.env.example to .deploy.env)"
[[ -n "$COMPOSE_DIR" ]] || die "COMPOSE_DIR is not set (copy .deploy.env.example to .deploy.env)"
command -v docker >/dev/null || die "docker is not installed"
command -v npm >/dev/null    || die "npm is not installed"

SHA="$(git rev-parse --short HEAD)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
ok "branch $BRANCH @ $SHA"
[[ "$BRANCH" == "main" ]] || warn "not on main — releasing an unreviewed commit"
if [[ -n "$(git status --porcelain)" ]]; then
  warn "working tree is dirty; the image will be tagged $SHA and will NOT match that commit"
fi

# Refuse to ship an unreleased commit that has never been CI'd.
if [ "$DRY_RUN" -eq 0 ] && [ "$BRANCH" == "main" ]; then
  git fetch --quiet origin main
  [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] \
    || die "local main is not pushed; push it so CI runs before you release"
  ok "local main matches origin/main (CI has run on this commit)"
fi

# Capture what is running NOW so the release can be reversed.
PREV_IMAGE=""
if [ "$DRY_RUN" -eq 0 ]; then
  PREV_IMAGE="$(ssh "$HOST" "docker ps -q --filter label=com.docker.compose.service=api | head -1 | xargs -r docker inspect --format '{{.Image}}'" 2>/dev/null || true)"
  [[ -n "$PREV_IMAGE" ]] && ok "currently running image: $PREV_IMAGE" || warn "could not identify the running container"
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  warn "DRY RUN — commands are printed, nothing is built, copied or deployed"
fi

# ---------------------------------------------------------------- 1. local checks
if [ "$SKIP_CHECKS" -eq 0 ]; then
  step "Backend tests"
  run "(cd BE && uv run pytest -q)"
  ok "pytest"

  step "Frontend typecheck + lint"
  run "(cd FE/chores && npm run lint && npm run build)"
  ok "npm run build / lint"
else
  warn "checks skipped (--skip-checks)"
fi

# ---------------------------------------------------------------- 2. build + push the API image
step "Build and push $IMAGE:$SHA ($PLATFORM)"
# --platform is mandatory: this Mac is arm64 and the VPS is amd64. Without it the host gets a
# manifest it cannot run. Two tags: immutable <sha> for rollback, `latest` for humans.
run "docker buildx build --platform $PLATFORM \
  -t '$IMAGE:$SHA' -t '$IMAGE:latest' --push BE"
ok "pushed $IMAGE:$SHA and $IMAGE:latest"

# ---------------------------------------------------------------- 3. build the static frontend
step "Build the frontend"
# VITE_API_BASE is baked in at build time from .env.production — a wrong value here ships a broken
# bundle even when the API is perfectly healthy.
run "(cd FE/chores && npm run build)"
ok "FE/chores/dist ready"

# ---------------------------------------------------------------- 4. back up the live database
step "Back up the database on $HOST"
STAMP="$(date +%Y%m%d-%H%M%S)"
remote "cp -v '$REMOTE_DB' '$REMOTE_DB.bak-$STAMP'"
ok "backup: $REMOTE_DB.bak-$STAMP"

# ---------------------------------------------------------------- 5. publish the frontend
step "Copy dist/ to $HOST:$WEB_ROOT"
if [ "$DRY_RUN" -eq 0 ]; then
  ssh "$HOST" "mkdir -p '$WEB_ROOT'"
  rsync -az --delete --exclude '.DS_Store' FE/chores/dist/ "$HOST:$WEB_ROOT/"
  ok "frontend published"
else
  printf '  $ rsync -az --delete FE/chores/dist/ %s:%s/\n' "$HOST" "$WEB_ROOT"
fi

# ---------------------------------------------------------------- 6. redeploy the API container
step "Redeploy the API with TAG=$SHA"
# `pull` is not optional — `up -d` alone reuses the cached image. `--wait` turns a crash loop into a
# non-zero exit instead of a silent "successful" deploy.
remote "cd '$COMPOSE_DIR' && export TAG='$SHA' && docker compose pull api && docker compose up -d --wait api"
ok "api container healthy"

# ---------------------------------------------------------------- 7. smoke test the public API
step "Smoke test $API_BASE"
SMOKE_FAILED=0
if [ "$DRY_RUN" -eq 1 ]; then
  warn "skipped during dry run"
else
  for path in "chores/home?expect=periodStart" "chores/dog-walking?expect=weekStart"; do
    endpoint="${path%%\?*}"
    needle="${path##*expect=}"
    body=""
    for attempt in 1 2 3 4 5 6 7 8 9 10; do
      body="$(curl -fsS --max-time 10 "$API_BASE/$endpoint" 2>/dev/null || true)"
      [[ "$body" == *"$needle"* ]] && break
      sleep 3
    done
    if [[ "$body" == *"$needle"* ]]; then
      ok "/$endpoint responds with $needle"
    else
      warn "/$endpoint did not return $needle"
      SMOKE_FAILED=1
    fi
  done
fi

# ---------------------------------------------------------------- summary
printf '\n\033[1mRelease summary\033[0m\n'
printf '  commit      %s (%s)\n' "$SHA" "$BRANCH"
printf '  image       %s:%s\n' "$IMAGE" "$SHA"
printf '  frontend    %s:%s/\n' "$HOST" "$WEB_ROOT"
printf '  db backup   %s.bak-%s\n' "$REMOTE_DB" "$STAMP"
if [[ -n "$PREV_IMAGE" ]]; then
  printf '\n  rollback:   cd %s && TAG=<previous-sha> docker compose up -d --wait api\n' "$COMPOSE_DIR"
  printf '              previous image id was %s\n' "$PREV_IMAGE"
fi

if [ "$SMOKE_FAILED" -eq 1 ]; then
  printf '\n\033[31m✗ Deployed, but the smoke test failed — check the logs before walking away:\033[0m\n'
  printf '  ssh %s "cd %s && docker compose logs --tail=100 api"\n' "$HOST" "$COMPOSE_DIR"
  exit 1
fi

printf '\n\033[32m✓ Release complete\033[0m\n'
