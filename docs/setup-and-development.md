# Setup and Development

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.12+ | Django backend |
| Node.js | 20+ | React frontend |
| Docker | Latest (optional) | Containerized development |
| npm | 9+ | Frontend package management |

---

## Docker Setup (Recommended for Quick Start)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine + Docker Compose (Linux)

### Steps

```bash
# From the project root
docker compose up --build
```

This builds both containers and starts the services:

1. Builds the Django backend image (`backend/Dockerfile`)
2. Builds the React frontend image (`frontend/Dockerfile`)
3. Installs all dependencies
4. Runs Django database migrations
5. Starts the Django dev server on port 8000
6. Starts the Vite dev server on port 5173

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Django Admin | http://localhost:8000/admin/ |

### Stop Containers

```bash
docker compose down
```

---

## Manual Backend Setup

### Steps

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# (Optional) Seed demo data
python manage.py seed_data

# Start the development server
python manage.py runserver
```

The backend API will be available at **http://localhost:8000/api/**.

### Verify Setup

```bash
# Run system checks
python manage.py check

# Run all tests
python manage.py test accounts.tests tickets.tests dashboard.tests
```

---

## Manual Frontend Setup

### Steps

```bash
# Navigate to the frontend directory
cd frontend

# Copy the environment file (adjust if needed)
cp .env.example .env

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will be available at **http://localhost:5173**.

### Proxy Configuration

The Vite dev server proxies `/api/*` requests to the Django backend. The proxy target defaults to `http://localhost:8000`. To override:

```bash
# frontend/.env
VITE_API_PROXY_TARGET=http://localhost:8000
```

---

## Seed Demo Data

```bash
cd backend

# Idempotent seed (creates only missing records)
python manage.py seed_data

# Reset all data and seed fresh
python manage.py seed_data --reset
```

### Demo Accounts

> **Warning:** These credentials are for demo/development only. Do not use in production.

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin1` | `Admin123!` |
| **Agent** | `agent1` | `Agent123!` |
| **Agent** | `agent2` | `Agent123!` |
| **Customer** | `customer1` | `Cust123!` |
| **Customer** | `customer2` | `Cust123!` |

### What the Seed Command Creates

- 5 users (1 admin, 2 agents, 2 customers)
- 5 ticket categories (Technical Support, Billing, Account Issue, Feature Request, General Inquiry)
- 15 tickets with various status/priority/assignment combinations
- Corresponding messages for each ticket

---

## Environment Variables

### Backend

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `DJANGO_SECRET_KEY` | Dev fallback | **Yes** in production | Django secret key |
| `DJANGO_DEBUG` | `True` | No | Debug mode (set to `False` for production) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | No | Comma-separated allowed hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Local origins | No | Comma-separated trusted origins |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_PROXY_TARGET` | `http://localhost:8000` | Backend URL for Vite proxy |

### Docker Compose

Variables set in `docker-compose.yml`:
- `DJANGO_DEBUG=True` — enables debug mode in Docker
- `VITE_API_PROXY_TARGET=http://backend:8000` — Docker service name as proxy target

---

## Ports

| Port | Service | Notes |
|------|---------|-------|
| 5173 | Vite dev server (frontend) | Proxies `/api/*` to backend |
| 8000 | Django development server (backend API) | |

---

## Common Development Commands

### Backend

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status (no changes)
python manage.py makemigrations --check --dry-run

# Run Django system checks
python manage.py check

# Open Django shell
python manage.py shell

# Open Django ORM shell with auto-imports
python manage.py shell_plus  # requires django-extensions
```

### Frontend

```bash
# Start dev server with hot reload
npm run dev

# TypeScript check (no emit)
npx tsc --noEmit

# Production build
npm run build

# Preview production build
npm run preview
```

---

## Database Reset

To completely reset the database:

```bash
cd backend

# Option 1: Using seed_data with reset flag
python manage.py seed_data --reset

# Option 2: Manual reset
rm db.sqlite3
python manage.py migrate
python manage.py seed_data
```

---

## Common Setup Problems and Fixes

### Problem: Port already in use

```
Error: listen tcp :8000: bind: address already in use
```

**Solution**: Stop the existing process or use a different port:

```bash
# Find process using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Start Django on an alternative port
python manage.py runserver 8001
```

### Problem: Virtual environment not activated

```
ModuleNotFoundError: No module named 'django'
```

**Solution**: Activate your virtual environment (see setup steps above).

### Problem: Migration conflicts

```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution**: Reset the database and re-run migrations:

```bash
python manage.py seed_data --reset
```

### Problem: CSRF errors in the browser console

```
CSRF Failed: CSRF token missing or incorrect
```

**Solutions**:
- Ensure the frontend calls `GET /api/accounts/csrf/` before any state-changing request (done automatically by `AuthContext` on mount).
- Verify `CSRF_TRUSTED_ORIGINS` includes the frontend origin.
- Check that the Axios request interceptor is reading the `csrftoken` cookie and sending `X-CSRFToken` header.

### Problem: CORS errors

```
Access to XMLHttpRequest at 'http://localhost:8000/...' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**: Ensure requests go through the Vite proxy (use `http://localhost:5173` for the frontend, not directly to the backend). The Vite proxy makes requests same-origin.

### Problem: Docker container exits immediately

**Solution**: Check logs:

```bash
docker compose logs
```

Common issues:
- Port already in use on the host
- Permission issues with volume mounts

---

## Suggested Demo Scenario

1. **Customer login** — `customer1 / Cust123!`
2. **View dashboard** — check ticket overview stats
3. **Create a new ticket** — fill in title, description, priority, category
4. **Logout**, then **Admin login** — `admin1 / Admin123!`
5. **View system dashboard** — see unassigned tickets, user stats
6. **Assign the new ticket** to an agent
7. **Check agent workload** — see the assignment reflected
8. **Logout**, then **Agent login** — `agent1 / Agent123!`
9. **View agent dashboard** — see assigned and unassigned pool
10. **Change ticket status** to IN_PROGRESS
11. **Reply to the ticket** with a message
12. **Logout**, then **Customer login** again
13. **View the ticket** — see the status change and agent's reply

---

## Related Documents

- [Testing](testing.md) — running tests and CI
- [Deployment](deployment.md) — production deployment guidance
- [Architecture](architecture.md) — system architecture overview
