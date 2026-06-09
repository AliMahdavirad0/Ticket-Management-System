# Ticket Frontend

Frontend for Ticket Management System built with React, Vite, TypeScript, TailwindCSS, and React Query.

## Features

- **JWT Authentication** — Login, register, token refresh with Axios interceptors
- **Role-Based UI** — Sidebar adapts for customer, agent, and admin roles
- **Dashboard** — Role-specific metrics (overview, priority breakdown, recent activity)
- **Ticket Listing** — Paginated list with status/priority filtering and search
- **Ticket Details** — Full ticket view with status/priority controls, agent assignment, and message thread
- **Create Ticket** — Form with category selection and priority
- **User Management** (Admin) — List users, update roles
- **Agent Workload** (Admin) — Per-agent ticket breakdown
- **Profile** — View and update profile, change password
- **Protected Routes** — Unauthenticated users redirected to login
- **Responsive Layout** — Sidebar + content area with Tailwind CSS

## Stack

- React 18
- TypeScript
- Vite
- TailwindCSS 3
- Axios
- @tanstack/react-query 5
- React Router DOM 6

## Project Structure

```
ticket-frontend/
├── src/
│   ├── api/                    # API service layer
│   │   ├── axiosClient.ts      # Axios instance + JWT interceptor
│   │   ├── authApi.ts          # Auth endpoints (login, register, profile, admin)
│   │   ├── ticketApi.ts        # Ticket CRUD, messages, categories
│   │   └── dashboardApi.ts     # Dashboard overview, agent workload
│   ├── components/             # Reusable UI components
│   │   ├── AppLayout.tsx       # Sidebar + content layout wrapper
│   │   ├── Badge.tsx           # Status/priority badges
│   │   ├── Button.tsx          # Button with loading state
│   │   ├── Card.tsx            # Content card container
│   │   ├── Input.tsx           # Text input
│   │   ├── Select.tsx          # Dropdown select
│   │   ├── Sidebar.tsx         # Navigation sidebar (role-aware)
│   │   └── Textarea.tsx        # Multi-line text input
│   ├── context/
│   │   └── AuthContext.tsx     # Global auth state
│   ├── hooks/                  # React Query hooks
│   │   ├── useAuth.ts          # Auth, profile, admin user hooks
│   │   ├── useTickets.ts       # Ticket, message, category hooks
│   │   └── useDashboard.ts     # Dashboard hooks
│   ├── pages/
│   │   ├── Login.tsx           # Login form
│   │   ├── Register.tsx        # Registration form
│   │   ├── Dashboard.tsx       # Role-based dashboard
│   │   ├── Tickets.tsx         # Paginated ticket list
│   │   ├── TicketDetails.tsx   # Single ticket + messages
│   │   ├── CreateTicket.tsx    # New ticket form
│   │   ├── Profile.tsx         # Profile + password change
│   │   ├── AdminUsers.tsx      # Admin: user management
│   │   ├── AdminAgentWorkload.tsx # Admin: agent workload
│   │   └── NotFound.tsx        # 404 page
│   ├── App.tsx                 # Router + protected routes
│   ├── main.tsx                # Entry point (QueryClient, Router, App)
│   ├── index.css               # Tailwind directives
│   └── vite-env.d.ts           # Vite type declarations
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── tsconfig.json
```

## Architecture

### Layered Data Flow

```
Pages ──→ Hooks (React Query) ──→ API Services (Axios) ──→ Backend API
            │
            └── Context (AuthContext)
```

| Layer | Responsibility |
|-------|---------------|
| **Pages** | UI rendering, form state, user interaction |
| **Hooks** | React Query wrappers: caching, loading/error states, cache invalidation |
| **API Services** | Typed HTTP calls via Axios client |
| **Context** | Global auth state (`isAuthenticated`, `setIsAuthenticated`, `logout`) |
| **Components** | Reusable, stateless UI primitives (Button, Card, Badge, Input, Select, Textarea) |

### State Management

- **Server state**: Managed by React Query with configurable `staleTime` values (30s for tickets, 1min for dashboard, 5min for profile/categories)
- **Auth state**: React Context (`AuthContext`) with localStorage-backed tokens
- **Tokens**: `access_token` and `refresh_token` stored in localStorage

## Setup

```bash
npm install
```

### Environment

Create `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api` | Backend API base URL |

## Run Development Server

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Routing

| Route | Page | Access |
|-------|------|--------|
| `/` | Redirect → `/dashboard` | — |
| `/login` | Login | Public |
| `/register` | Register | Public |
| `/dashboard` | Dashboard | Authenticated |
| `/profile` | Profile | Authenticated |
| `/tickets` | Ticket List | Authenticated |
| `/tickets/create` | Create Ticket | Authenticated |
| `/tickets/:id` | Ticket Details | Authenticated |
| `/admin/users` | User Management | Authenticated (admin UI) |
| `/admin/agent-workload` | Agent Workload | Authenticated (admin UI) |
| `*` | 404 Not Found | — |

Protected routes use a `<Protected>` wrapper that redirects to `/login` when `access_token` is absent.

## API Integration

### Axios Client (`api/axiosClient.ts`)

- Base URL from `VITE_API_URL` env var
- **Request interceptor**: Attaches `Authorization: Bearer <token>` from localStorage
- **Response interceptor**: On 401, attempts token refresh via `/accounts/refresh/` and retries the original request. If refresh fails, clears tokens and redirects to `/login`

### API Modules

| Module | Endpoints |
|--------|-----------|
| `authApi.ts` | Login, register, profile, change password, admin user management |
| `ticketApi.ts` | Ticket CRUD, status/priority changes, assignment, messages, categories |
| `dashboardApi.ts` | Dashboard overview, agent workload |

## Hooks Reference

### `useAuth.ts`

| Hook | Type | Description |
|------|------|-------------|
| `useLogin` | Mutation | Login, tokens stored externally |
| `useRegister` | Mutation | Register + redirect to /login |
| `useLogout` | Function | Clear tokens + query cache + redirect |
| `useProfile` | Query | Current user profile (5min staleTime) |
| `useUpdateProfile` | Mutation | Update profile + cache update |
| `useChangePassword` | Mutation | Change password |
| `useIsAuthenticated` | Helper | `true` if access_token in localStorage |
| `useUserRole` | Helper | Returns user role string from profile |
| `useUsers` | Query | Admin: list all users |
| `useUpdateUserRole` | Mutation | Admin: update user role |
| `useAvailableAgents` | Query | Admin: agents by workload |

### `useTickets.ts`

| Hook | Type | Description |
|------|------|-------------|
| `useTickets` | Query | Paginated list with filters |
| `useTicket` | Query | Single ticket by ID |
| `useCreateTicket` | Mutation | Create + invalidate list |
| `useUpdateTicket` | Mutation | Update + invalidate |
| `useDeleteTicket` | Mutation | Delete + invalidate |
| `useChangeTicketStatus` | Mutation | Status change + invalidate |
| `useChangeTicketPriority` | Mutation | Priority change + invalidate |
| `useAssignTicket` | Mutation | Admin: assign agent |
| `useTicketStatistics` | Query | Ticket stats (1min staleTime) |
| `useTicketMessages` | Query | Messages for a ticket |
| `useAddTicketMessage` | Mutation | Add message to ticket |
| `useCategories` | Query | All categories (5min staleTime) |
| `useCreateCategory` | Mutation | Admin: create category |

### `useDashboard.ts`

| Hook | Type | Description |
|------|------|-------------|
| `useDashboardOverview` | Query | Role-based dashboard (1min staleTime) |
| `useAgentWorkload` | Query | Admin: agent workload (1min staleTime) |

## Default Backend Endpoints

- `/api/accounts/login/`
- `/api/accounts/register/`
- `/api/accounts/profile/`
- `/api/tickets/`
- `/api/dashboard/`

## Suggested Backend

Backend expected:

- Django REST Framework
- JWT Authentication
- CORS enabled
- REST endpoints
