# Frontend Service (FE)

## Overview
The frontend is a React + Vite app for the chores service. It provides a login/signup flow, a protected weekly timetable UI, admin stats, and a settings page. The UI talks to the backend through a configured API base URL.

## Key Technologies
- React 19
- Vite
- TypeScript
- Tailwind CSS
- React Router 7
- react-hook-form
- Chart.js
- Lucide icons
- Custom UI components

## Project Structure
- `src/main.tsx` — app bootstrap, routing, providers
- `src/context/UserContext.ts` — user auth state and current user fetch
- `src/pages/Login.tsx` — login screen
- `src/pages/SignUp.tsx` — signup screen
- `src/pages/Home.tsx` — timetable view and week navigation
- `src/pages/Settings.tsx` — user settings
- `src/pages/Stats.tsx` — admin-only stats page
- `src/components/ProtectedRoute.tsx` / `ProtectedAdminRoute.tsx` — route guards
- `src/utils/fetch.ts` — constructs API URLs from `VITE_API_BASE`

## Features
- login and signup flow
- secure cookie-based API requests using `credentials: "include"`
- protected app routes for authenticated users
- admin-only stats route
- weekly timetable display with previous/next week navigation
- assign self to timeslots
- summary and allocation status
- form validation for signup/login

## Environment Variables
- `VITE_API_BASE` — backend base URL, e.g. `http://localhost:8000/api`
- `VITE_DISABLE_GUEST` — disable guest mode on FE. If missing will default to false.

## Setup
1. `cd FE/chores`
2. Install dependencies:
   - `npm install`
   - or `npm ci`
3. Create a `.env` file with:
   - `VITE_API_BASE=http://localhost:8000/api`
4. Run locally:
   - `npm run dev`

## Build
- `npm run build`

## Routes
- `/login` — login page
- `/sign-up` — signup page
- `/home` — main timetable dashboard
- `/settings` — user settings
- `/stats` — admin-only statistics

## Notes
- The frontend uses `BrowserRouter` and client-side routing.
- API requests are built with `fetchURL()` from `src/utils/fetch.ts`.
- Auth state is refreshed whenever the login token changes.
- Protected routes depend on the user object from `UserContext`.