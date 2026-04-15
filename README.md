# Chores App

## What it does
This repository contains a small chores scheduling app with:
- a backend API for user auth, timetable management, and email notifications
- a frontend React app for login, signup, weekly schedule display, and admin stats
- a dog walking timetable workflow where users can assign themselves to morning/evening slots
- scheduled emails for daily walker summaries and weekly reminders

## Architecture
- `BE/` — Python FastAPI backend
- `FE/chores/` — React + Vite frontend
- `docker-compose.yml` — runs the backend service with SQLite persistence

## Technologies
### Backend
- Python 3.13
- FastAPI
- SQLModel / SQLite
- JWT auth with `python-jose`
- password hashing with `bcrypt` / `passlib`
- scheduled jobs with `APScheduler`
- email via Resend API
- dependency/lock management with `uv`

### Frontend
- React 19
- Vite
- TypeScript
- Tailwind CSS
- React Router 7
- react-hook-form
- Chart.js
- Lucide icons

## Setup

### Backend
1. `cd BE`
2. Install `uv` if not installed
3. Create a `.env` file with:
   - `SECRET_KEY=...`
   - `RESEND_API_KEY=...`
   - optional: `DB_PATH=/app/data/database.db`
   - optional: `TEST_USER_EMAIL=...`
   - optional: `TEST_USER_PASSWORD=...`
4. Install dependencies:
   - `uv install`
5. Sync with lockfile:
   - `uv sync --no-dev --frozen --no-install-project`
6. Run locally:
   - `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*" --root-path "/api"`

### Frontend
1. `cd FE/chores`
2. Install packages:
   - `npm install`
   - or `npm ci`
3. Create `.env` with:
   - `VITE_API_BASE=http://localhost:8000/api`
4. Start the app:
   - `npm run dev`

### Docker
To run the backend with Docker:
- `docker compose up --build`

## Notes
- Backend API root is mounted at `/api`
- Frontend uses `VITE_API_BASE` to call the backend
- Backend persists data to `BE/data/database.db` when using Docker Compose
- Frontend routing is client-side via React Router

## Useful paths
- Backend: `BE/app/`
- Frontend: `FE/chores/src/`