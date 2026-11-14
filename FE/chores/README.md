# Frontend Service (FE)

React + Vite SPA for the chores app: login/signup, two protected chore sections (weekly dog rota and
fortnightly home chores), and an admin-only stats page. All API calls go to the backend configured via
`VITE_API_BASE` using the auth cookie.

> Working with an AI agent? Read [`AGENTS.md`](./AGENTS.md) in this folder plus the repo root
> [`AGENTS.md`](../../AGENTS.md) for conventions, data-flow contracts and gotchas.

## Stack

React 19 · Vite (`rolldown-vite`) · TypeScript (strict) · Tailwind CSS 4 · React Router 7 ·
react-hook-form · Chart.js / react-chartjs-2 · lucide-react · shadcn/ui primitives · ESLint 9

## Layout

| Path | Purpose |
| --- | --- |
| `src/main.tsx` | bootstrap: `UserProvider` → `EditPanelProvider` → `BrowserRouter` → route table |
| `src/pages/DogChores.tsx` | weekly dog rota, week navigation, days-to-assign counter, summary popover |
| `src/pages/HomeChores.tsx` | fortnightly home chores, period navigation, chores-to-claim counter, join/leave |
| `src/pages/Login.tsx` | cookie login + Guest Mode button |
| `src/pages/SignUp.tsx` | registration (react-hook-form) |
| `src/pages/Stats.tsx` | admin-only bar chart of shifts per person |
| `src/pages/Settings.tsx` | placeholder stub |
| `src/components/MergedDayCell.tsx` | one day column, Morning + Evening cells |
| `src/components/HomeChoreCard.tsx` | one chore, its claimants, and the join/leave toggle |
| `src/components/EditPanel.tsx` | modal for assigning/unassigning a dog-rota slot |
| `src/components/Summary.tsx` | per-person counts popover; each page passes its own counts |
| `src/components/Navbar.tsx`, `NavMenu.tsx`, `NavLink.tsx` | top bar, profile menu, nav links |
| `src/components/ProtectedRoute.tsx`, `ProtectedAdminRoute.tsx` | route guards + page chrome |
| `src/context/UserContext.ts` | auth state (`user`, `token` toggle) |
| `src/context/EditContext.ts` | which slot the edit panel is open for |
| `src/utils/fetch.ts` | `fetchURL(path)` → `${VITE_API_BASE}/${path}` |
| `src/utils/timetable.ts` | dog-rota types, API→UI transform, Monday/week math |
| `src/utils/homeChores.ts` | home-chore types, fortnight anchoring/labels, claimant counts |
| `src/utils/dates.ts` | calendar-safe date helpers (`parseISODate`, `formatISODate`, `addDays`) |
| `src/components/ui/` | shadcn/ui primitives (button, card, input) |

## Routes

| Path | Guard | Page |
| --- | --- | --- |
| `/` | — | redirects to `/login` |
| `/login` | public (redirects to `/chores/dog-walking` when logged in) | `Login` |
| `/sign-up` | public | `SignUp` |
| `/chores/dog-walking` | `ProtectedRoute` | `DogChores` |
| `/chores/home` | `ProtectedRoute` | `HomeChores` |
| `/home` | `ProtectedRoute` | redirects to `/chores/dog-walking` |
| `/settings` | `ProtectedRoute` | `Settings` (stub) |
| `/stats` | `ProtectedAdminRoute` | `Stats` |

## How auth works here

There is no token in JS. `POST /token` sets an `HttpOnly` cookie; every request uses
`credentials: "include"`. `UserContext` fetches `GET /user` and exposes `{ user, setUser, token,
setToken }` where `token` is a **boolean toggle** that re-triggers the fetch (login does
`setToken(!token)`). Logout calls `POST /logout` then `setUser(undefined)` and navigates to `/login`.

Role-dependent UI: `["admin", "user"].includes(user?.role ?? "")` controls edit affordances;
`user.role === "admin"` controls the Stats nav link. Route guards are UX only — the API is
authoritative.

## Environment variables

Copy [`.env.example`](./.env.example) to `.env.development` (or `.env.production`). Values are
**inlined at build time**.

| Variable | Required | Example |
| --- | --- | --- |
| `VITE_API_BASE` | ✅ | `https://local.app.com:8000` (dev) or `https://chores.dempseypalaciotascon.com/api` (prod) |
| `VITE_DISABLE_GUEST` | — | string `"true"` hides the Guest Mode button |

## Setup & run

```bash
cd FE/chores
npm ci
npm run dev      # https://local.app.com:5173
```

Dev runs over HTTPS with the certs in `./local_cert` (gitignored — regenerate with mkcert) and binds
`0.0.0.0:5173`; `local.app.com` must resolve to `127.0.0.1` in `/etc/hosts`.

## Build & lint

```bash
npm run lint     # eslint 9 flat config
npm run build    # tsc -b && vite build   ← the typecheck gate
npm run preview
```

There is no test suite; lint + build are the checks.

## Notes / gotchas

- Guest credentials (`guest@example.com` / `guestpassword`) are hardcoded in `pages/Login.tsx` and must
  match the backend's `create_guest_user()`.
- `verbatimModuleSyntax` + `erasableSyntaxOnly` are enabled: use `import type` and avoid enums.
  `noUnusedLocals`/`noUnusedParameters` mean unused imports break `npm run build`.
- Date navigation goes through `src/utils/dates.ts` (`addDays`) rather than raw millisecond sums or
  `setDate()`: adding days via the `Date` constructor keeps the calendar date stable across DST.
- `NavLink` matches exactly or with a trailing slash, so `/chores/dog-walking` cannot light up
  `/chores/home`. Keep that matcher if you add routes.
- `HomeChores` claims with an explicit `claimed` flag and uses the `PATCH` response as the new state;
  there is no edit modal for home chores — `EditPanel` is dog-rota only.
- `components/Snackbar.tsx`, `context/SnackbarContext.ts` and `pages/Settings.tsx` are unused stubs.
