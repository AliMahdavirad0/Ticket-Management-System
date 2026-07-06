# Ticket Management System

Full-stack role-based ticket management system with JWT authentication.

| Layer | Stack |
|-------|-------|
| **Backend** | Django 6, DRF, SimpleJWT, SQLite |
| **Frontend** | React 18, TypeScript, TanStack Query, Tailwind CSS |
| **API Docs** | Swagger UI / ReDoc (drf-spectacular) |

---

## Quick Start

## Docker Setup

This project is fully Dockerized. The frontend (React + Vite) and backend (Django) can be built and run using Docker Compose.
Prerequisites

- Before running the project, make sure the following software is installed:

     - Docker Desktop

     - Docker Compose (included with Docker Desktop)

#### Verify the installation:

```bash
docker --version
docker compose version
```

#### From the project root directory, execute:

    `docker compose up --build`


#### Docker Compose will automatically:

    Build the Django backend image

    Build the React frontend image

    Install all dependencies

    Run Django database migrations

    Start the backend server

    Start the frontend development server


#### Access the Application

- Frontend : http://localhost:5173

- Backend API : http://localhost:8000

- Swagger API Documentation : http://localhost:8000/api/docs/

- Admin Panel : http://localhost:8000/admin/

#### Stopping the Project

- To stop all running containers:
    `docker compose down`

#### Rebuilding the Project

- If source files or Dockerfiles are modified:
    `docker compose up --build`

#### Creating a Django Superuser (Optional)

- If access to the Django admin panel is needed:
    `docker compose exec backend python manage.py createsuperuser`

- Follow the prompts to create the administrator account.

#### Rebuilding from Scratch

- If a clean build is required:
    ```bash
    docker compose down --volumes --rmi all
    docker compose up --build
    ```

- This removes containers, images, and volumes before rebuilding the project.

---
---
---

### Backend

```bash
cd ticketProject
python -m venv .venv && source .venv/bin/activate   # or `.venv\Scripts\Activate.ps1` on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API is available at **`http://localhost:8000/api/`**.

### Frontend

```bash
cd ticket-frontend
cp .env.example .env              # edit VITE_API_URL if needed
npm install
npm run dev
```

App is available at **`http://localhost:5173`**.

---

## Project Structure

```
DjangoProject/
├── ticketProject/                # Django backend
│   ├── accounts/                 # User model, auth views, user management
│   │   ├── services/
│   │   │   └── user_service.py  # User business logic layer
│   │   ├── management/commands/
│   │   │   └── seed_data.py     # Database seeding
│   │   ├── serializers.py       # Auth & user serializers
│   │   ├── permissions.py       # Role-based permission classes
│   │   ├── auth_views.py        # JWT login/refresh with user payload
│   │   └── views.py             # Registration, profile, admin user management
│   ├── tickets/                 # Ticket CRUD, messages, categories
│   │   ├── services/
│   │   │   ├── ticket_service.py   # Ticket business logic
│   │   │   └── message_service.py  # Message business logic
│   │   ├── serializers.py       # Ticket, message, category serializer hierarchy
│   │   ├── permissions.py       # Object-level permissions per role
│   │   └── views.py             # ViewSets with custom actions
│   ├── dashboard/               # Role-based dashboards and metrics
│   │   ├── services/
│   │   │   └── dashboard_service.py  # Metrics aggregation
│   │   ├── serializers.py       # Dashboard response serializers
│   │   └── views.py             # Overview and agent workload endpoints
│   ├── ticketProject/           # Settings, root URL config, exception handler
│   ├── manage.py
│   └── requirements.txt
├── ticket-frontend/             # React frontend
│   ├── src/
│   │   ├── api/                 # Axios clients and API functions
│   │   ├── components/          # Reusable UI (Button, Card, Input, etc.)
│   │   ├── context/             # AuthContext (isAuthenticated, logout)
│   │   ├── hooks/               # TanStack Query hooks (useAuth, useTickets, etc.)
│   │   └── pages/               # Route pages (Login, Dashboard, Tickets, etc.)
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Architecture

The backend follows a **layered architecture** with clear separation of concerns:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **View** | `*/views.py` | HTTP handling, serialization, permission enforcement |
| **Service** | `*/services/*.py` | Business logic, validation, data aggregation |
| **Model** | `*/models.py` | Data schema, ORM relationships |
| **Serializer** | `*/serializers.py` | Input/output data transformation |

Views delegate business logic to service classes (`TicketService`, `MessageService`, `UserService`, `DashboardService`), keeping controllers thin and business rules testable.

---

## Authentication Flow

1. **Register** → `POST /api/accounts/register/` → creates a `customer` user
2. **Login** → `POST /api/accounts/login/` → returns `{ access, refresh, user }`
3. **Authenticate** → frontend stores tokens in `localStorage`, attaches `Authorization: Bearer <token>` to every request
4. **Refresh** → Axios interceptor auto-refreshes on 401 responses
5. **Logout** → clears tokens from localStorage, redirects to `/login`

---

## User Roles

| Role | Access Summary |
|------|----------------|
| **customer** | Own tickets & messages; create tickets; update while OPEN |
| **agent** | Assigned + unassigned pool; change status/priority |
| **admin** | All tickets, users, categories, assignments, global metrics |

---

## API Endpoints

Interactive docs at `http://localhost:8000/api/docs/` (Swagger) or `http://localhost:8000/api/redoc/` (ReDoc).

### Authentication & Accounts

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/accounts/register/` | POST | ✗ | Register a new customer |
| `/api/accounts/login/` | POST | ✗ | Obtain JWT tokens (+ user data) |
| `/api/accounts/refresh/` | POST | ✗ | Refresh JWT token |
| `/api/accounts/profile/` | GET | ✓ | Current user profile + stats |
| `/api/accounts/profile/update/` | PUT/PATCH | ✓ | Update email, first/last name |
| `/api/accounts/change-password/` | POST | ✓ | Change password |
| `/api/accounts/users/` | GET | Admin | List all users with statistics |
| `/api/accounts/users/{id}/` | GET | Admin | User detail |
| `/api/accounts/users/{id}/role/` | PATCH | Admin | Update user role |
| `/api/accounts/agents/available/` | GET | Admin | Agents sorted by workload |

### Tickets

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/tickets/` | GET | ✓ | List tickets (role-filtered) |
| `/api/tickets/` | POST | ✓ | Create ticket |
| `/api/tickets/{id}/` | GET | ✓ | Ticket detail with messages |
| `/api/tickets/{id}/` | PATCH | ✓ | Update ticket |
| `/api/tickets/{id}/` | DELETE | ✓ | Delete ticket (owner/OPEN or admin) |
| `/api/tickets/{id}/change_status/` | PATCH | Agent+ | Change status |
| `/api/tickets/{id}/assign/` | PATCH | Admin | Assign agent |
| `/api/tickets/{id}/change_priority/` | PATCH | Agent+ | Change priority |
| `/api/tickets/statistics/` | GET | ✓ | Role-scoped ticket statistics |

### Messages & Categories

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/messages/` | GET | ✓ | List messages (role-filtered) |
| `/api/messages/` | POST | ✓ | Create message on a ticket |
| `/api/categories/` | GET | ✓ | List categories |
| `/api/categories/` | POST | Admin | Create category |
| `/api/categories/{id}/` | PUT/PATCH/DELETE | Admin | Modify/delete category |

### Dashboard

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/dashboard/` | GET | ✓ | Role-based overview with metrics |
| `/api/dashboard/agents/` | GET | Admin | Agent workload breakdown |

---

## Database Schema

The project uses four custom tables (plus Django's built-in auth tables for groups and permissions).

### Tables

#### `accounts_user` — Custom user model (extends Django's `AbstractUser`)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `BIGINT` | `PK`, auto-increment |
| `password` | `VARCHAR(128)` | not null |
| `last_login` | `DATETIME` | nullable |
| `is_superuser` | `BOOLEAN` | not null |
| `username` | `VARCHAR(150)` | `UNIQUE`, not null |
| `first_name` | `VARCHAR(150)` | nullable |
| `last_name` | `VARCHAR(150)` | nullable |
| `email` | `VARCHAR(254)` | nullable |
| `is_staff` | `BOOLEAN` | not null |
| `is_active` | `BOOLEAN` | not null, default `true` |
| `date_joined` | `DATETIME` | not null |
| `role` | `VARCHAR(20)` | not null, `CHECK(role IN ('customer','agent','admin'))`, default `'customer'` |

Inherited Many-to-Many: `groups` → `auth_group`, `user_permissions` → `auth_permission`

---

#### `tickets_ticketcategory` — Ticket categories

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `BIGINT` | `PK`, auto-increment |
| `name` | `VARCHAR(100)` | `UNIQUE`, not null |

---

#### `tickets_ticket` — Support tickets

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `BIGINT` | `PK`, auto-increment |
| `title` | `VARCHAR(255)` | not null |
| `description` | `TEXT` | not null |
| `status` | `VARCHAR(20)` | not null, `CHECK(status IN ('OPEN','IN_PROGRESS','RESOLVED','CLOSED'))`, default `'OPEN'` |
| `priority` | `VARCHAR(20)` | not null, `CHECK(priority IN ('LOW','MEDIUM','HIGH','CRITICAL'))`, default `'MEDIUM'` |
| `user_id` | `BIGINT` | `FK → accounts_user.id`, not null, `ON DELETE CASCADE` |
| `assigned_agent_id` | `BIGINT` | `FK → accounts_user.id`, nullable, `ON DELETE SET NULL` |
| `category_id` | `BIGINT` | `FK → tickets_ticketcategory.id`, nullable, `ON DELETE SET NULL` |
| `created_at` | `DATETIME` | not null, auto-set on create |
| `updated_at` | `DATETIME` | not null, auto-updated |

**Indexes:**
- `idx_ticket_status` on `status`
- `idx_ticket_priority` on `priority`
- `idx_ticket_created_at` on `created_at`

---

#### `tickets_ticketmessage` — Messages on a ticket

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `BIGINT` | `PK`, auto-increment |
| `ticket_id` | `BIGINT` | `FK → tickets_ticket.id`, not null, `ON DELETE CASCADE` |
| `sender_id` | `BIGINT` | `FK → accounts_user.id`, not null, `ON DELETE CASCADE` |
| `message` | `TEXT` | not null |
| `created_at` | `DATETIME` | not null, auto-set on create |

---

### Entity Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| `accounts_user` → `tickets_ticket` (via `user_id`) | **One-to-Many** | A user can own many tickets; a ticket belongs to one user |
| `accounts_user` → `tickets_ticket` (via `assigned_agent_id`) | **One-to-Many** | An agent can be assigned many tickets; a ticket has one assigned agent (nullable) |
| `accounts_user` → `tickets_ticketmessage` (via `sender_id`) | **One-to-Many** | A user can send many messages; a message has one sender |
| `tickets_ticketcategory` → `tickets_ticket` (via `category_id`) | **One-to-Many** | A category can have many tickets; a ticket has one category (nullable) |
| `tickets_ticket` → `tickets_ticketmessage` (via `ticket_id`) | **One-to-Many** | A ticket can have many messages; a message belongs to one ticket |

---

## Frontend Architecture

| File | Purpose |
|------|---------|
| `api/axiosClient.ts` | Axios instance with JWT interceptor and auto-refresh |
| `context/AuthContext.tsx` | Global auth state (`isAuthenticated`, `setIsAuthenticated`, `logout`) |
| `hooks/useAuth.ts` | `useLogin`, `useRegister`, `useProfile`, `useLogout` |
| `hooks/useTickets.ts` | `useTicket`, `useTickets`, `useCreateTicket`, `useTicketMessages` |
| `hooks/useDashboard.ts` | `useDashboardOverview` |

---

## Environment Variables

### Backend (`ticketProject/ticketProject/settings.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | (dev fallback) | Secret key |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | (empty) | Comma-separated |

### Frontend (`ticket-frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api` | Backend API base URL |

---

## CORS

Already configured for `http://localhost:5173`. Edit `CORS_ALLOWED_ORIGINS` in `ticketProject/ticketProject/settings.py` to add production domains.

---

## Seeding Data

The project includes a management command to populate the database with sample users and tickets:

```bash
cd ticketProject
python manage.py seed_data
```

---

## Testing

```bash
cd ticketProject
python manage.py test accounts.tests tickets.tests dashboard.tests
```

---

THIS IS A TEST FOR CI