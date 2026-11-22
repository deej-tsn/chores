# AGENTS.md

Instructions for AI coding agents (and new contributors) working in this repository. Read this first,
then the package-level file for the area you are touching:

- Backend work → [`BE/AGENTS.md`](./BE/AGENTS.md)
- Frontend work → [`FE/chores/AGENTS.md`](./FE/chores/AGENTS.md)
- Human-oriented overview → [`README.md`](./README.md)

---

## 1. What this project is

A household dog-walking rota. React SPA + FastAPI API + SQLite, with Resend email notifications
scheduled in-process. Two packages, no monorepo tooling, no shared type generation.

| Package | Path | Stack | Entry point |
| --- | --- | --- | --- |
| Backend | `BE/` | Python 3.13, FastAPI, SQLModel/SQLite, uv, APScheduler, Resend | `BE/app/main.py` |
| Frontend | `FE/chores/` | React 19, Vite (rolldown), TS strict, Tailwind 4, React Router 7 | `FE/chores/src/main.tsx` |

## 2. Golden rules

1. **Run the checks before claiming done.** Backend: `cd BE && uv run pytest -v`. Frontend:
   `cd FE/chores && npm run build`.
   Frontend lint is **clean** — a new `npm run lint` error is yours. Backend has a 6-finding Ruff
   baseline (see [`README.md` → Known gaps](./README.md#known-gaps)); do not silently bundle those
   fixes into an unrelated change. Never report success on code you did not run.
2. **Never commit secrets.** `BE/.env`, `BE/data/`, `BE/local_cert/`, `FE/chores/local_cert/` are
   gitignored. If you need env shape, edit `.env.example`, not `.env`.
3. **Do not touch generated/vendored paths:** `BE/.venv/`, `**/__pycache__/`, `FE/chores/node_modules/`,
   `FE/chores/dist/`, `FE/chores/package-lock.json` (regenerate, don't hand-edit).
4. **The auth cookie is `Secure; SameSite=None`.** Local development is HTTPS-only; never "fix" a
   local auth problem by relaxing cookie flags or CORS to `*` with credentials.
5. **Backend authorization is authoritative.** Frontend route guards are UX only. Any new
   privileged endpoint must use `Depends(require_admin)` (or an explicit role check) server-side.
   Keep role-list checks in sync with the FE (`["admin", "user"]`) so UI and API agree.
6. **Keep `README.md` API/route tables in sync** whenever you add, remove, or rename an endpoint or page.
7. **Prefer the smallest correct diff.** This is a small app; do not introduce state libraries, ORM
   migration frameworks, or test runners without being asked.
8. **No migrations exist.** A model change means the local `BE/data/database.db` must be recreated.
   Say so explicitly when you change a model.

## 3. Repository layout (annotated)

```
BE/app/main.py                     every route + startup lifecycle; single module by design
BE/app/config.py                   pydantic-settings Settings (cached via lru_cache)
BE/app/utils/database/db.py        SQLModel models (User, UserDB, Timetable, HomeChore,
                                   HomeChoreAssignment, HomeChoreClaim), engine, week + fortnight
                                   seeding, query helpers: get_dog_walkers_for_today, get_email_list,
                                   add_weeks_dates, add_period_assignments, get_fortnight_start,
                                   get_home_chores_for_period, get_last_monday, create_guest_user
BE/app/utils/auth/jwt.py           create_access_token, get_current_user, require_admin
BE/app/utils/auth/password.py      passlib bcrypt hashing
BE/app/utils/notifications/resend.py  APScheduler jobs + HTML email templates
BE/app/utils/stats/stats.py        per-person shift counts since START_DATE (2025-12-08)
BE/tests/conftest.py               in-memory SQLite + fake Settings + dependency overrides
FE/chores/src/main.tsx             providers + route table (single source of truth for routes)
FE/chores/src/context/UserContext.ts   auth state; refetches /user when `token` toggles
FE/chores/src/context/EditContext.ts   which dog-rota cell the edit panel is editing
FE/chores/src/utils/fetch.ts       fetchURL("/path") → `${VITE_API_BASE}/path`
FE/chores/src/utils/timetable.ts   dog-rota types, API→UI transform, Monday/week math
FE/chores/src/utils/homeChores.ts  home-chore types, fortnight anchoring, claimant counts
FE/chores/src/utils/dates.ts       calendar-safe date helpers shared by both sections
FE/chores/src/types/user.ts        User / Token / TokenData shapes
deploy/docker-compose.vps.yml      THE production compose file (also at /root/docker-compose-scripts on the VPS)
docker-compose.yml                 local/dev api container — never the production definition
scripts/release.sh                 release: build+push image, rsync FE, redeploy, smoke test
```

## 4. Domain vocabulary

Use these terms consistently in code, tests, and docs:

| Term | Meaning |
| --- | --- |
| **week start** | the Monday of a week; `get_last_monday()` normalises any date to it |
| **slot** | one `Timetable` row = `(day, time)` where `time ∈ {Morning, Evening}` |
| **assigned** | `Timetable.assigned` FK → `userdb.id`; `NULL` = unassigned |
| **dog rota** | the weekly dog-walking section: `Timetable` rows, one walker per slot |
| **fortnight / period** | 14 days anchored to a Monday; `period_start` is its first day |
| **chore catalogue** | `HomeChore` rows (name, description, `active`); never hardcode chore names |
| **assignment** | one `HomeChoreAssignment` = a chore in one fortnight |
| **claim** | one `HomeChoreClaim` = a person owning an assignment; several claims are allowed |
| **roles** | `guest`, `read-only-user` (signup default), `user`, `admin` |
| **guest mode** | shared read-only login, `guest@example.com` / `guestpassword`, toggle `DISABLE_GUEST_MODE` |
| **seeding** | `add_weeks_dates()` for a dog week; `add_period_assignments()` for a chores fortnight |

## 5. Environment & commands

```bash
# Backend
cd BE
uv sync                                  # install from uv.lock (never `pip install`)
uv run pytest -v                         # tests
make run                                 # uvicorn --reload with local TLS
uv run ruff check . && uv run ruff format .

# Frontend
cd FE/chores
npm ci                                   # prefer ci over install for lockfile fidelity
npm run dev                              # vite dev server, https://local.app.com:5173
npm run build                            # tsc -b && vite build  (passes)
npm run lint                             # clean — a new error is yours

# Release (from repo root; needs .deploy.env with HOST/WEB_ROOT/COMPOSE_DIR)
./scripts/release.sh                     # build → push → rsync FE → compose pull/up --wait → smoke test
./scripts/release.sh --dry-run           # print every command, touch nothing
```

Local hostnames: `/etc/hosts` needs `127.0.0.1 local.app.com`. Backend dev API base is
`https://local.app.com:8000` (root_path is stripped locally); production is
`https://chores.dempseypalaciotascon.com/api`.

> **Releases go through `scripts/release.sh` only.** Do not hand-run the steps it encapsulates. It
> exists because three failures are silent otherwise: building arm64 on this Mac for an amd64 VPS,
> running `docker compose up -d` without `pull` (keeps the cached image), and a crash-looping container
> still exiting 0. It also pins `TAG=<git-sha>` so a release can actually be rolled back.

> **Always use `https://local.app.com:5173`, never `https://localhost:5173`.** Both resolve, but the
> backend's CORS allow-list and the `local_cert/` TLS certs are issued for `local.app.com` only. The
> browser sends the *origin string* verbatim, so `localhost` is a different origin and gets
> `No 'Access-Control-Allow-Origin' header is present`. When a CORS error appears, fix the URL you
> opened — do **not** add `localhost` variants to `origins` in `BE/app/main.py`.

## 6. Cross-cutting contracts

**Auth flow**
1. `POST /token` (form-encoded `username`/`password`) → sets `access_token` cookie.
2. SPA never reads the token; it calls `GET /user` and gets JWT claims (`sub`, `first_name`,
   `second_name`, `colour`, `role`, `iat`, `exp`).
3. `get_current_user` re-validates that the email still exists in `UserDB` on every request.
4. `POST /logout` clears the cookie; the frontend sets `user = undefined` and navigates to `/login`.

**Dog rota flow**
1. `GET /chores/dog-walking?week=YYYY-MM-DD` → `{ weekStart, timetable: [{id, day, time, assigned}] }`
   (`assigned` is the user's **first name** or `null`).
2. `convertDataToTimeTableType()` in the SPA pivots that flat list into
   `{ Monday: { Morning: Day, Evening: Day }, ... }`.
3. Editing a cell opens `EditPanel`, which sends `PATCH /chores/dog-walking` and uses the response as
   the new client state — no refetch needed.

**Home chores flow**
1. `GET /chores/home?period=YYYY-MM-DD` → `{ periodStart, chores: [{id, chore, description,
   claimed_by, claimed_by_me}] }`; `period` is normalised to the fortnight's Monday.
2. `HomeChores.tsx` claims inline (no modal) with `PATCH /chores/home`
   `{ assignmentID, claimed, period }`. `claimed` is explicit, so the call is idempotent and can never
   remove someone else's claim.
3. Chores can be shared, so joining an already-claimed chore is the normal case — do **not** reuse
   `MergedDayCell`'s "only if empty or mine" rule here.

**Wire-format asymmetry to respect:** the API returns snake_case dicts for users/stats/chores but
`weekStart`/`periodStart` camelCase, and signup accepts `surename` (sic) as the payload field name for
surname.
Do not "clean these up" in isolation; a rename is a breaking API + frontend change.

## 7. Definition of done

- [ ] Tests/checks pass (see rule 1) and no *new* lint errors were introduced.
- [ ] New endpoints: implemented, permission-checked, covered by `BE/tests/`, and added to both
      `README.md` and `BE/README.md` API tables.
- [ ] New pages/routes: registered in `main.tsx`, guarded appropriately, listed in both READMEs.
- [ ] New env var: added to `BE/app/config.py` **and** `.env.example` **and** the README tables.
- [ ] No secrets, no debug `print`/`console.log` left behind.
- [ ] If you changed a model, the "delete the SQLite file" consequence is called out in your summary.

## 8. Where things go

| You are adding... | Put it in |
| --- | --- |
| a route | `BE/app/main.py` (import helpers rather than inlining queries) |
| a reusable DB/domain query | `BE/app/utils/database/db.py` |
| email/scheduling logic | `BE/app/utils/notifications/resend.py` |
| a settings/env knob | `BE/app/config.py` + `BE/.env.example` |
| a page | `FE/chores/src/pages/*.tsx` + register in `main.tsx` |
| a shared component | `FE/chores/src/components/*.tsx` (shadcn primitives stay in `components/ui/`) |
| app-wide state | `FE/chores/src/context/*` (one context per concern) |
| API↔UI type mapping | `FE/chores/src/utils/timetable.ts` (dogs), `utils/homeChores.ts` (home chores) / `src/types/` |
| date arithmetic | `FE/chores/src/utils/dates.ts` — never hand-roll day maths in a component |
