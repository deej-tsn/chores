# Backend Service (BE)

## Overview
The backend is a FastAPI service for the chores app. It exposes API endpoints under `/api`, stores users and timetable data in SQLite, issues JWT tokens via secure cookies, and sends scheduled reminder/summary emails with Resend.

## Key Technologies
- Python 3.13+
- FastAPI
- SQLModel / SQLite
- python-jose JWT
- bcrypt / passlib
- APScheduler
- Resend email API
- python-dotenv
- `uv` for dependency and lockfile management

## Project Structure
- `app/main.py` — FastAPI app, routes, startup lifecycle
- `app/config.py` — settings from `.env` via `pydantic-settings`
- `app/utils/database/db.py` — DB models, session, helper utilities
- `app/utils/auth/jwt.py` — JWT creation and auth dependencies
- `app/utils/notifications/resend.py` — scheduled email notifications

## Features
- user signup and login
- cookie-based JWT authentication
- admin-only endpoints for user list and stats
- timetable read and update
- automatic weekly timetable seeding
- daily dog walker summary emails
- Sunday reminder emails
- development test user creation on startup

## Environment Variables
Required:
- `SECRET_KEY`
- `RESEND_API_KEY`

Optional:
- `DB_PATH` — defaults to `data/database.db`
- `TEST_USER_EMAIL` — used in `DEV` mode
- `TEST_USER_PASSWORD` — used in `DEV` mode
- `ENVIRONMENT` — defaults to `PROD`
- `DISABLE_GUEST_MODE` - optional (defaults to `False` if not present)

## Setup
1. Install `uv` if not already installed.
2. Run:
   - `uv install`
3. Sync dependencies with the lock file:
   - `uv sync --no-dev --frozen --no-install-project`

## Running
1. Create a `.env` file with required settings.
2. Start the FastAPI app with Uvicorn pointing to `app.main:app`.
3. On startup:
   - database tables are created
   - notification scheduler starts
   - in `DEV`, weekly dates and a test user are seeded

## Main Endpoints
- `POST /api/token` — login, returns token in cookie
- `POST /api/users/` — create user and login
- `GET /api/users/` — admin-only list users
- `GET /api/users/{user_id}` — admin-only user detail
- `GET /api/user` — current user info from token
- `GET /api/logout` — clear auth cookie
- `GET /api/timetable` — get current week timetable
- `PATCH /api/timetable` — assign user to a timeslot
- `GET /api/count` — admin-only stats since start

## Notes
- The app root path is configured as `"/api"` in `app/main.py`.
- Scheduled emails use Resend credentials from env vars.
- Timetable rows are created automatically for each week when needed.