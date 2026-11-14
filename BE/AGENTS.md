# BE/AGENTS.md — Backend

Scope: everything under `BE/`. Read [`../AGENTS.md`](../AGENTS.md) first.

## Stack & tooling

- Python **3.13** (`app/.python-version`), FastAPI + Starlette, SQLModel/SQLAlchemy 2, SQLite.
- **uv** owns dependencies. Use `uv sync` (never `pip install`), `uv run <cmd>`, `uv add <pkg>`.
  Commit `uv.lock` with any dependency change.
- Ruff for lint+format. pytest for tests (`testpaths = ["tests"]`, `pythonpath = "."`).
- `bcrypt==4.0.1` is pinned deliberately — passlib 1.7.4 breaks on bcrypt ≥ 4.1. Do not bump it
  casually; verify `get_password_hash` / `verify_password` still work if you do.

## Layout rules

- **Routes live in `app/main.py`.** It is intentionally one module. When it grows, split by
  `APIRouter` in `app/routers/` *and* update `AGENTS.md` + `README.md` in the same change.
- **Queries and models live in `app/utils/database/db.py`.** Handlers should call helpers
  (`get_email_list`, `get_dog_walkers_for_today`, `add_weeks_dates`, ...) or inline a small
  `select()`; don't duplicate a join that already exists as a helper.
- **Settings only via `app/config.py`.** Never `os.getenv` in a handler. Note `db.py` does read
  `DB_PATH` via `os.getenv` at import time (engine creation) — that is the one accepted exception;
  it happens before `Settings` is available.
- **Side effects on startup go in `on_startup()`** (DB init, scheduler, guest/test seeding) and must
  stay ordered: settings validation → `create_db_and_tables()` → scheduler → guest → DEV seeding.

## Patterns to follow

Dependency injection — do not re-implement auth inside handlers:

```python
@app.get("/thing")
def read_thing(session: SessionDep, user: TokenData = Depends(get_current_user)):
    ...

@app.get("/admin-thing")
def read_admin_thing(session: SessionDep, _: UserDB = Depends(require_admin)):
    ...
```

Role checks for the *current actor* are done against the DB (see `require_admin`), not the JWT claim,
because roles can change without the token being reissued. `PATCH /timetable` additionally restricts
assignment to `role in {"admin", "user"}` and returns **401** (not 403) for forbidden roles — the
existing tests assert that, so keep it consistent unless you update the tests intentionally.

Response models — return Pydantic/SQLModel types (`TimetableData`, `TimetablePublic`, `User`), not raw
dicts. `session.refresh()` after `add`/`commit` when the created row is returned.

Date handling — all week logic goes through `get_last_monday()` / `week_dependency()`. Never compute
"start of week" inline; a DST/`setDate` bug already happened once (see `hotfix/fix-dst-issue` and the
`ONE_WEEK_MS` constant in `Home.tsx`).

Errors — `HTTPException(status_code=..., detail="...")`. Existing status conventions:
400 wrong credentials / duplicate email, 401 unauthenticated or bad role, 403 admin-only,
404 missing user.

## Testing

- `tests/conftest.py` provides `session` (in-memory SQLite with one seeded week, `StaticPool`) and
  `client` (dependency overrides for `get_session` and `get_settings_dep`, `base_url="https://testserver"`).
- Add permission-matrix cases to `tests/test_auth.py` (`@pytest.mark.parametrize("role", TEST_ROLES)`)
  and behaviour cases to a new `test_<area>.py`.
- `tests/test_ready.py` patches names on `app.main` (`create_db_and_tables`, `start_notifications_scheduler`,
  `create_guest_user`, `add_weeks_dates`, `create_test_user`, `get_settings`). If you rename or move
  startup hooks, update those patch targets or the tests will silently stop asserting anything.
- Never let tests reach `data/database.db`, the network, or Resend. Mock `resend.Emails.send`.

```bash
uv run pytest -v            # whole suite — currently 26 passed
uv run pytest tests/test_auth.py -v
make test                   # same, via Makefile
```

Use `uv run pytest`, not `.venv/bin/python -m pytest`: the checked-in `.venv` can be stale/partial
(no pytest installed) while `uv run` resolves the locked environment.

## Running locally

```bash
make run     # .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
             # with --ssl-keyfile/--ssl-certfile from ./local_cert
```

`.env` needs `SECRET_KEY` and `RESEND_API_KEY`. With `ENVIRONMENT=DEV` you must also set
`TEST_USER_EMAIL` + `TEST_USER_PASSWORD` or startup raises `KeyError`. The TLS certs in `local_cert/`
are gitignored — regenerate them (mkcert or openssl) if missing; the frontend dev server uses its own
copy in `FE/chores/local_cert/`.

## Gotchas

- `Field(..., env="NAME")` in `config.py` is legacy pydantic-settings v1 style; v2 matches env names
  case-insensitively against the **field name**, so `DISABLE_GUEST_MODE` works by coincidence. If you
  add a var that maps to an awkward name, use `validation_alias`/`alias` explicitly.
- `app/.python-version` sits inside `app/`, not `BE/` — a stray `uv` command may pick the wrong
  interpreter; run uv from `BE/`.
- CI (`.github/workflows/tests.yml`) uses Python 3.11 while `requires-python = ">=3.13"`. If tests
  fail in CI but pass locally, check this first.
- The Dockerfile `CMD` historically carried a trailing space after a `\` line continuation; keep
  continuations clean.
- Schema changes are destructive: `SQLModel.metadata.create_all` does not migrate. Delete
  `data/database.db` locally, and plan the data migration for the deployed volume manually.
- The notification scheduler runs inside the API process at 09:00 daily and Sunday 21:00. Multiple
  workers/replicas ⇒ duplicate emails.
- `@app.on_event("startup")` is deprecated by FastAPI. Migrating to a `lifespan` context means also
  rewriting `tests/test_ready.py` (it patches `app.main.on_startup` and `app.main.get_settings`), so do
  it as a dedicated change.
- Local TLS: `make run` hard-codes `./local_cert/local.app.com{,-key}.pem`. Missing/expired certs are
  the most common "cannot connect" cause; they are gitignored, so each clone regenerates them.
