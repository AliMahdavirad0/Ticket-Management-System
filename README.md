# Ticket Management System

A full-stack role-based ticket management system with session authentication.

| Layer | Stack |
|-------|-------|
| **Backend** | Django 6, DRF, Session Auth, SQLite |
| **Frontend** | React 18, TypeScript, TanStack Query, Tailwind CSS, Vite |
| **API Docs** | Swagger UI / ReDoc (drf-spectacular) |

---

## Features

- Role-based access control: **Customer**, **Agent**, **Admin**
- Ticket CRUD with status workflow and priority levels
- Ticket messaging per role permissions
- Role-based dashboard with statistics
- Admin user management with role assignment
- Agent workload monitoring
- Category management
- Session-based authentication with CSRF protection
- Pagination, filtering, search, and ordering
- Interactive API documentation (Swagger / ReDoc)
- Docker Compose for local demo
- CI pipeline (GitHub Actions)

## Roles and Permissions

| Role | Access |
|------|--------|
| **Customer** | Own tickets and messages; create tickets; update while OPEN; delete own OPEN tickets |
| **Agent** | Assigned tickets + unassigned pool; change status/priority; message on accessible tickets |
| **Admin** | All tickets, users, categories, assignments, global dashboard metrics |

### Status Transitions

```
OPEN → IN_PROGRESS, CLOSED
IN_PROGRESS → RESOLVED, CLOSED
RESOLVED → IN_PROGRESS, CLOSED
CLOSED → OPEN (admin only)
```

### Closed Ticket Rules

- No new messages can be added to a CLOSED ticket.
- Only admins can reopen a CLOSED ticket (CLOSED → OPEN).

---

## Architecture

The backend follows a **layered architecture**:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **View** | `*/views.py` | HTTP handling, permission enforcement |
| **Service** | `*/services/*.py` | Business logic, validation, data aggregation |
| **Model** | `*/models.py` | Data schema, ORM relationships |
| **Serializer** | `*/serializers.py` | Request/response transformation |

Views delegate business logic to service classes (`TicketService`, `MessageService`, `UserService`, `DashboardService`), keeping controllers thin and business rules testable.

---

## Quick Start with Docker

```bash
docker compose up --build
```

This will:
1. Build the Django backend image
2. Build the React frontend image
3. Install all dependencies
4. Run Django database migrations
5. Start both servers

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Django Admin | http://localhost:8000/admin/ |

### Stop

```bash
docker compose down
```

---

## Manual Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend API: **http://localhost:8000/api/**

### Frontend

```bash
cd frontend

# Copy and adjust if needed
cp .env.example .env

npm install
npm run dev
```

Frontend: **http://localhost:5173**

The Vite dev server proxies `/api/*` to the backend. For local development without Docker, the proxy target defaults to `http://localhost:8000`. Set `VITE_API_PROXY_TARGET` in `.env` to override.

---

## Seed Demo Data

```bash
cd backend
python manage.py seed_data
```

To reset and reseed from scratch:

```bash
python manage.py seed_data --reset
```

### Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin1` | `Admin123!` |
| **Agent** | `agent1` | `Agent123!` |
| **Agent** | `agent2` | `Agent123!` |
| **Customer** | `customer1` | `Cust123!` |
| **Customer** | `customer2` | `Cust123!` |

> **Warning:** These credentials are for demo/development only. Do not use in production.

---

## API Documentation

Interactive docs are available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

### Key Endpoints

#### Authentication (Session-based)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/accounts/csrf/` | No | Get CSRF cookie |
| `GET` | `/api/accounts/session/` | No | Check session status |
| `POST` | `/api/accounts/session/login/` | No | Login (creates session) |
| `POST` | `/api/accounts/session/logout/` | Yes | Logout (destroys session) |
| `POST` | `/api/accounts/register/` | No | Register new customer |

#### Profile

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/accounts/profile/` | Yes | Current user profile + stats |
| `PATCH` | `/api/accounts/profile/update/` | Yes | Update profile |
| `POST` | `/api/accounts/change-password/` | Yes | Change password |

#### Tickets

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/tickets/` | Yes | List tickets (role-filtered) |
| `POST` | `/api/tickets/` | Yes | Create ticket |
| `GET` | `/api/tickets/{id}/` | Yes | Ticket detail with messages |
| `PATCH` | `/api/tickets/{id}/` | Yes | Update ticket |
| `DELETE` | `/api/tickets/{id}/` | Yes | Delete ticket |
| `PATCH` | `/api/tickets/{id}/change_status/` | Agent+ | Change status |
| `PATCH` | `/api/tickets/{id}/assign/` | Admin | Assign agent |
| `PATCH` | `/api/tickets/{id}/change_priority/` | Agent+ | Change priority |
| `GET` | `/api/tickets/statistics/` | Yes | Ticket statistics |

#### Messages & Categories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/messages/?ticket={id}` | Yes | List messages |
| `POST` | `/api/messages/` | Yes | Create message |
| `GET` | `/api/categories/` | Yes | List categories |
| `POST` | `/api/categories/` | Admin | Create category |
| `DELETE` | `/api/categories/{id}/` | Admin | Delete category |

#### Dashboard

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/dashboard/` | Yes | Role-based overview |
| `GET` | `/api/dashboard/agents/` | Admin | Agent workload |

#### Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/accounts/users/` | Admin | List users (paginated) |
| `PATCH` | `/api/accounts/users/{id}/role/` | Admin | Update user role |
| `GET` | `/api/accounts/agents/available/` | Admin | Available agents |

---

## Authentication Flow

This project uses **Django Session Authentication** with CSRF protection:

1. Frontend calls `GET /api/accounts/csrf/` on mount to obtain the `csrftoken` cookie.
2. User logs in via `POST /api/accounts/session/login/` with `username` + `password`.
3. Django validates credentials, creates a session, and sets the `sessionid` (HttpOnly) cookie.
4. The `sessionid` cookie is sent automatically on subsequent requests.
5. For state-changing requests (POST/PUT/PATCH/DELETE), the frontend reads the `csrftoken` cookie and sends its value as the `X-CSRFToken` header (handled automatically by the Axios interceptor).
6. Logout calls `POST /api/accounts/session/logout/` to destroy the session.

**There is no JWT.** Tokens are not stored in localStorage. The session cookie is HttpOnly and cannot be read by JavaScript, providing protection against XSS attacks.

### CSRF Retry Logic

The Axios response interceptor checks for actual CSRF failures (responses containing "CSRF" in the error detail) before triggering a retry with a fresh token. Permission errors (403 without CSRF detail) are not retried.

---

## Tests

### Backend (69 tests)

```bash
cd backend
python manage.py test accounts.tests tickets.tests dashboard.tests
```

### Per app

```bash
python manage.py test accounts.tests
python manage.py test tickets.tests
python manage.py test dashboard.tests
```

### Frontend

```bash
cd frontend
npm run build    # TypeScript check + production build
```

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | Dev fallback | Secret key (required in production) |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | (empty) | Comma-separated hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | (empty) | Comma-separated origins |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_PROXY_TARGET` | `http://localhost:8000` | Backend URL for Vite proxy |

---

## Project Structure

```
├── backend/                # Django backend
│   ├── accounts/                 # User model, auth views, user management
│   │   ├── services/user_service.py
│   │   ├── management/commands/seed_data.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   └── session_views.py
│   ├── tickets/                  # Ticket CRUD, messages, categories
│   │   ├── services/ticket_service.py
│   │   ├── services/message_service.py
│   │   ├── serializers.py
│   │   └── permissions.py
│   ├── dashboard/                # Role-based dashboards and metrics
│   │   ├── services/dashboard_service.py
│   │   └── serializers.py
│   ├── backend/            # Settings, root URL config
│   ├── manage.py
│   └── requirements.txt
├── frontend/              # React frontend
│   ├── src/
│   │   ├── api/                  # Axios clients and API functions
│   │   ├── components/           # Reusable UI components
│   │   ├── context/              # AuthContext
│   │   ├── hooks/                # TanStack Query hooks
│   │   └── pages/                # Route pages
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

---

## Documentation

Comprehensive technical documentation is available in the [`docs/`](docs/) directory.

| Document | Description |
|----------|-------------|
| [Documentation Index](docs/README.md) | Full index with navigation and reading order |
| [Architecture](docs/architecture.md) | System architecture, backend layers, request lifecycle |
| [C4 Model](docs/c4-model.md) | Context, container, and component diagrams |
| [Backend Reference](docs/backend.md) | Django apps, services, serializers, views, permissions |
| [Frontend Reference](docs/frontend.md) | React structure, hooks, API clients, components |
| [Database](docs/database.md) | Data models, fields, relationships, ER diagram |
| [API Reference](docs/api-reference.md) | Complete endpoint documentation with examples |
| [Authentication & RBAC](docs/authentication-and-rbac.md) | Session auth flow, CSRF, roles, permission matrix |
| [Ticket Workflow](docs/ticket-workflow.md) | Status transitions, lifecycle, role-based rules |
| [Setup & Development](docs/setup-and-development.md) | Installation, configuration, troubleshooting |
| [Testing](docs/testing.md) | Test structure, running tests, CI execution |
| [Deployment](docs/deployment.md) | Docker setup, production recommendations |
| [Limitations & Roadmap](docs/limitations-and-roadmap.md) | Current limitations and planned improvements |

---

## Suggested Demo Scenario (5-7 minutes)

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

## Current Limitations

- SQLite database (swap to PostgreSQL for production)
- No email notifications
- No file attachments
- No real-time updates (polling-based)
- No rate limiting
- Session-based auth (not suitable for API-only/mobile clients without proxy)
