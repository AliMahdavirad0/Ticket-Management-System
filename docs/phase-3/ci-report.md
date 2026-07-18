# CI Report — Phase 3

**Workflow file:** `.github/workflows/ci.yml`  
**Evidence date:** 2026-07-18  

## Scope of this report

This report documents what the CI workflow is **configured** to run.  
**No successful remote GitHub Actions run is claimed here** — this Phase 3 package was prepared locally without GitHub execution evidence.

Local backend tests were executed separately; see `backend-test-results.md` and `evidence/backend-test-run.txt`.

---

## Triggers

```yaml
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]
```

---

## Backend pipeline (`jobs.backend`)

| Step | Command / Action | Purpose |
|------|------------------|---------|
| Checkout | `actions/checkout@v4` | Clone repository on runner |
| Set up Python | `actions/setup-python@v5` with Python **3.12** | Provide interpreter |
| Install dependencies | `pip install -r requirements.txt` (cwd: `backend`) | Install Django/DRF and test deps |
| Migrations check | `python manage.py makemigrations --check --dry-run` | Fail if model changes lack migrations |
| Migrate | `python manage.py migrate` | Apply schema to CI database |
| System checks | `python manage.py check` | Django deployment/system checks |
| Run tests | `python manage.py test accounts.tests tickets.tests dashboard.tests` | Execute backend unit/API tests |

Working directory for run steps: **`backend`**.

---

## Frontend pipeline (`jobs.frontend`)

| Step | Command / Action | Purpose |
|------|------------------|---------|
| Checkout | `actions/checkout@v4` | Clone repository |
| Set up Node.js | `actions/setup-node@v4` with Node **20**, npm cache on `frontend/package-lock.json` | Provide Node toolchain |
| Install dependencies | `npm ci` (cwd: `frontend`) | Clean, lockfile-faithful install |
| TypeScript check | `npx tsc --noEmit` | Static type validation (no emit) |
| Production build | `npm run build` | `tsc && vite build` production bundle |

Working directory for run steps: **`frontend`**.

---

## What CI does **not** do (from workflow file)

- No deployment step
- No frontend unit/E2E tests
- No Docker build in CI
- No coverage upload / artifact publishing configured
- No scheduled runs

---

## Local verification note

Backend test command matching CI was run locally on 2026-07-18:

```text
python manage.py test accounts.tests tickets.tests dashboard.tests
→ Ran 77 tests … OK
```

Frontend `tsc` / `npm run build` were **not** executed as part of this Phase 3 evidence pack unless separately recorded; do not assume frontend CI green without a log.
