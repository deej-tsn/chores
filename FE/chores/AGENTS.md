# FE/chores/AGENTS.md — Frontend

Scope: everything under `FE/chores/`. Read [`../../AGENTS.md`](../../AGENTS.md) first.

## Stack & tooling

- React **19**, Vite (**rolldown-vite** via `overrides`), TypeScript **strict**, Tailwind CSS **v4**
  (`@tailwindcss/vite`, no `tailwind.config.js` — theme lives in `src/index.css`).
- React Router **7** (`react-router`, *not* `react-router-dom`).
- shadcn/ui primitives in `src/components/ui/` (`components.json` describes the setup: style
  `new-york`, `@/components/ui` alias, lucide icons). Add new primitives with the shadcn CLI/config
  rather than hand-rolling, and keep `cn()` from `@/lib/utils` for class merging.
- Package manager: npm (only `package-lock.json` exists). Prefer `npm ci`.

```bash
npm ci
npm run dev      # https://local.app.com:5173 (TLS certs in ./local_cert, host 0.0.0.0)
npm run lint     # eslint 9 flat config
npm run build    # tsc -b && vite build  ← also the typecheck gate
npm run preview
```

> **Open `https://local.app.com:5173`, never `https://localhost:5173`.** `vite.config.ts` binds
> `0.0.0.0:5173` so both hosts serve the app, but the TLS certs are issued for `local.app.com` and the
> backend CORS allow-list (`BE/app/main.py`) contains only `https://local.app.com:5173`. Using
> `localhost` produces a CORS `No 'Access-Control-Allow-Origin' header` error on `/token`. Fix the URL,
> not the CORS list.

There is **no test runner**. `npm run build` (tsc + vite) is the gate and currently passes.

**Lint baseline:** `npm run lint` is clean (the 6 errors previously documented here were fixed). A new
error or warning is yours — fix it in the change that introduces it.

## Layout rules

- `src/main.tsx` is the single route table. Every page must be registered there (`ProtectedRoute` for
  logged-in pages, `ProtectedAdminRoute` for admin-only pages, public routes outside both).
- Pages → `src/pages/`. Reusable UI → `src/components/`. Primitives → `src/components/ui/`.
  Cross-page state → `src/context/`.
- Import paths: use the `@/` alias (`@/components/ui/card`, `@/utils/fetch`). Relative
  `../` imports exist in older files; prefer `@/` in new code.
- `tsconfig.app.json` has `verbatimModuleSyntax` + `erasableSyntaxOnly` ⇒ **type-only imports must use
  `import type { X }`**, and no enums / parameter properties. `noUnusedLocals` and
  `noUnusedParameters` are on, so unused imports fail the build.

## Data flow contract

- **All API calls go through `fetchURL()`** (`src/utils/fetch.ts`) →
  `${import.meta.env.VITE_API_BASE}/path`. Never hardcode a host or `/api`.
- **Always pass `credentials: "include"`.** Auth is an HttpOnly cookie; there is no `Authorization`
  header and the token is never stored in JS.
- Auth state lives in `UserContext`: `{ user, setUser, token, setToken }`. `token` is a **boolean
  toggle**, not a JWT — flipping it re-runs the `useEffect` that fetches `GET /user`. To re-fetch the
  current user, toggle it (`setToken(!token)`); to log out, `setUser(undefined)`.
- Dog rota shape: the API returns a flat list; `convertDataToTimeTableType()` pivots it into
  `TimeTableDict` keyed by **full weekday names** (`Monday`…`Sunday`, Sunday-first indexing handled
  inside). Mutations (`PATCH /chores/dog-walking`) return the full refreshed timetable — reuse that
  response instead of refetching.
- Home chores shape: a flat list per fortnight, `{ id, chore, description, claimed_by, claimed_by_me }`.
  `PATCH /chores/home` takes an explicit `claimed` boolean and returns the refreshed period. Never infer
  "mine" by comparing first names — use `claimed_by_me`.
- Date math: week math lives in `src/utils/timetable.ts` (`getMonday`, `formatDate`, `diffInDates`,
  `daysOfWeek`); fortnight anchoring in `src/utils/homeChores.ts`; and the calendar-safe helpers
  (`parseISODate`, `formatISODate`, `addDays`) in `src/utils/dates.ts`. Use those — `new
  Date("YYYY-MM-DD")` is UTC and `toISOString()` can slip a day near midnight.

## Authorization in the UI

`ProtectedRoute` / `ProtectedAdminRoute` are UX guards only — the API enforces real permissions.
`ProtectedRoute` renders the `Navbar` + `<main className="mt-24 ...">` chrome, so pages should not add
their own page frame. Role-dependent affordances follow the existing pattern:

```ts
const isAuthorized = ["admin", "user"].includes(user?.role ?? "");
```

Roles: `guest`, `read-only-user` (signup default), `user`, `admin`. `guest`/`read-only-user` see both
chore sections read-only; only admins see the Stats nav link.

## Styling

- Tailwind utilities inline; the palette is warm (cream `#FFF8F2`, amber `#E59D50` / `#FFB974`,
  brown text `#3A2F2F` / `#6A5F5D`). Reuse these values rather than inventing new hex codes.
- Animations come from `tailwindcss-animated` / `tw-animate-css`
  (`animate-fade-up animate-duration-500`).
- Component variants: `class-variance-authority` as in `components/ui/button.tsx`.
- Prettier config is in `.prettierrc`; the repo formats on save with prettier-eslint. Match existing
  formatting in the file you touch instead of reformatting whole files (diffs stay reviewable).

## Gotchas

- **Guest credentials are duplicated** here (`pages/Login.tsx`: `guest@example.com` / `guestpassword`)
  and in the backend's `create_guest_user()`. Change both or neither.
- `VITE_DISABLE_GUEST` must be the string `"true"` — the check is `=== "true"`.
- `VITE_*` vars are inlined at **build** time; changing `.env.production` requires rebuilding the
  Docker image, not just restarting.
- `react-hooks` lint rules are `recommended-latest`: `useEffect` dependency arrays must be honest.
  `DogChores.tsx` and `HomeChores.tsx` intentionally run their fetch once via a stable `useCallback`
  with `[]`; if you extract that fetch into a component/util, keep the behaviour identical.
- Unused scaffolding that is safe to delete but currently compiles: `components/Snackbar.tsx`,
  `context/SnackbarContext.ts` (it exports a second `EditPanelProvider` that must not be mounted),
  and `pages/Settings.tsx` (stub).
- `EditPanel` is only rendered for `admin`/`user` roles from `DogChores.tsx`; the cell click also
  re-checks the role. Keep both checks if you refactor. Home chores deliberately have no modal: the
  card's Join/Leave button is the whole interaction.
- `NavLink` matches a route exactly or with a trailing slash — not a bare `startsWith` — so one section
  cannot appear active on a sibling route. Keep that if you add routes.
- `exhaustive-deps` warnings in `SignUp.tsx` are the remaining known ones; fixing them means
  restructuring the trigger effect, so do it deliberately rather than blindly adding dependencies.
