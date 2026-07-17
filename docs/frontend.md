# Frontend

## Technology Stack

| Technology | Version |
|------------|---------|
| React | 18.3 |
| TypeScript | 5.4 |
| Vite | 5.x |
| TanStack Query (React Query) | 5.x |
| Axios | 1.6 |
| React Router DOM | 6.26 |
| Tailwind CSS | 3.4 |
| PostCSS | 8.4 |

## Application Structure

```
frontend/
├── src/
│   ├── api/                    # API service modules
│   │   ├── axiosClient.ts      # Axios config, CSRF interceptor
│   │   ├── authApi.ts          # Auth, profile, user management
│   │   ├── ticketApi.ts        # Tickets, messages, categories
│   │   └── dashboardApi.ts     # Dashboard endpoints
│   ├── components/             # Reusable UI components
│   │   ├── AppLayout.tsx       # Layout wrapper with sidebar
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   ├── Badge.tsx           # Status/priority/role badge
│   │   ├── Button.tsx          # Button with variants
│   │   ├── Card.tsx            # Card container
│   │   ├── Input.tsx           # Text input
│   │   ├── Select.tsx          # Dropdown select
│   │   └── Textarea.tsx        # Textarea input
│   ├── context/
│   │   └── AuthContext.tsx      # Auth state management
│   ├── hooks/
│   │   ├── useAuth.ts          # Auth/profile/user query hooks
│   │   ├── useTickets.ts       # Ticket query & mutation hooks
│   │   └── useDashboard.ts     # Dashboard query hooks
│   ├── pages/
│   │   ├── Login.tsx           # Login page
│   │   ├── Register.tsx        # Registration page
│   │   ├── Dashboard.tsx       # Role-based dashboard
│   │   ├── Tickets.tsx         # Ticket list
│   │   ├── TicketDetails.tsx   # Single ticket detail
│   │   ├── CreateTicket.tsx    # Create new ticket
│   │   ├── Profile.tsx         # User profile
│   │   ├── AdminUsers.tsx      # Admin: user management
│   │   ├── AdminAgentWorkload.tsx  # Admin: agent workload
│   │   ├── AdminCategories.tsx # Admin: category management
│   │   └── NotFound.tsx        # 404 page
│   ├── App.tsx                 # Root with routing and auth guards
│   ├── main.tsx                # Entry point
│   └── index.css               # Tailwind imports
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── package.json
├── .env                        # Environment variables
└── .env.example                # Environment template
```

---

## Page Routing

Defined in `frontend/src/App.tsx` using React Router DOM `Routes`:

| Path | Component | Access |
|------|-----------|--------|
| `/` | Redirect → `/dashboard` | Anyone |
| `/login` | `Login` | Public |
| `/register` | `Register` | Public |
| `/dashboard` | `Dashboard` | Authenticated |
| `/profile` | `Profile` | Authenticated |
| `/tickets` | `Tickets` | Authenticated |
| `/tickets/create` | `CreateTicket` | Authenticated |
| `/tickets/:id` | `TicketDetails` | Authenticated |
| `/admin/users` | `AdminUsers` | Admin only |
| `/admin/agent-workload` | `AdminAgentWorkload` | Admin only |
| `/admin/categories` | `AdminCategories` | Admin only |
| `*` | `NotFound` | Anyone |

### Route Guards

- **`Protected`**: Checks `isAuthenticated` from `AuthContext`. Shows a loading spinner during session check. Redirects to `/login` if unauthenticated.
- **`AdminRoute`**: Same as `Protected` plus checks `user.role === 'admin'`. Redirects to `/dashboard` if not admin.

---

## Authentication Context

`frontend/src/context/AuthContext.tsx`

The `AuthProvider` component manages authentication state using React Context:

| State | Type | Description |
|-------|------|-------------|
| `user` | `UserMinimal \| null` | Current user data |
| `isLoading` | `boolean` | True during initial session check |
| `isAuthenticated` | `boolean` | Whether a valid session exists |

| Method | Description |
|--------|-------------|
| `login(username, password)` | Calls `sessionLogin`, updates state on success |
| `logout()` | Calls `sessionLogout`, clears query cache, resets state |
| `refreshSession()` | Re-checks session (used after registration) |

### Initialization Flow (on app mount)

1. `authApi.fetchCsrfToken()` — GET `/api/accounts/csrf/` to set the `csrftoken` cookie
2. `authApi.checkSession()` — GET `/api/accounts/session/` to check for an existing session
3. If authenticated: store user data, set `isAuthenticated = true`
4. If not: set `isAuthenticated = false`
5. `isLoading` is set to `false` after the check completes

---

## Axios Configuration

`frontend/src/api/axiosClient.ts`

### Instance Setup

```typescript
const axiosClient = axios.create({
  baseURL: '/api',             // proxied by Vite → Django
  withCredentials: true,       // send sessionid + csrftoken cookies
  headers: { 'Content-Type': 'application/json' },
})
```

### Request Interceptor

Reads the `csrftoken` cookie (non-HttpOnly) and attaches it as the `X-CSRFToken` header on POST/PUT/PATCH/DELETE requests.

### Response Interceptor

| Status | Action |
|--------|--------|
| 401 | Redirect to `/login` (unless already on `/login`) |
| 403 with "CSRF" in detail | Retry once: fetch fresh CSRF token, resend request |
| Other 403 | Pass through (permission error, not CSRF) |

The CSRF retry uses a `Set<string>` to avoid infinite retry loops — each URL+method combination is retried at most once per session.

---

## TanStack Query Hooks

### `useAuth.ts` — Auth and User Management Hooks

| Hook | Query Key | Description |
|------|-----------|-------------|
| `useProfile()` | `['profile']` | Get current user profile (5 min stale time) |
| `useUpdateProfile()` | — | Mutation: update profile, updates cache on success |
| `useChangePassword()` | — | Mutation: change password |
| `useIsAuthenticated()` | — | Returns auth boolean from context |
| `useUser()` | — | Returns current user object from context |
| `useUserRole()` | — | Returns current user role string |
| `useUsers(params)` | `['users', params]` | Admin: list users with search/role filters (30s stale) |
| `useUpdateUserRole()` | — | Admin: mutation to change user role |
| `useAvailableAgents()` | `['availableAgents']` | Admin: get agents sorted by workload |

### `useTickets.ts` — Ticket Hooks

| Hook | Query Key | Description |
|------|-----------|-------------|
| `useTickets(params)` | `['tickets', params]` | Paginated ticket list (30s stale) |
| `useTicket(id)` | `['ticket', id]` | Single ticket with messages |
| `useCreateTicket()` | — | Mutation: creates ticket, invalidates ticket lists |
| `useUpdateTicket()` | — | Mutation: updates ticket, refreshes cache |
| `useDeleteTicket()` | — | Mutation: deletes ticket, invalidates lists |
| `useChangeTicketStatus()` | — | Mutation: changes status, invalidates related queries |
| `useChangeTicketPriority()` | — | Mutation: changes priority, invalidates related queries |
| `useAssignTicket()` | — | Mutation: assigns agent, invalidates related queries |
| `useTicketStatistics()` | `['ticketStatistics']` | Ticket statistics (1 min stale) |
| `useTicketMessages(id)` | `['ticketMessages', id]` | Messages for a ticket |
| `useAddTicketMessage()` | — | Mutation: adds message, invalidates messages query |
| `useCategories()` | `['categories']` | Category list (5 min stale) |
| `useCreateCategory()` | — | Mutation: creates category |
| `useDeleteCategory()` | — | Mutation: deletes category |

### `useDashboard.ts` — Dashboard Hooks

| Hook | Query Key | Description |
|------|-----------|-------------|
| `useDashboardOverview()` | `['dashboardOverview']` | Role-based dashboard (1 min stale) |
| `useAgentWorkload()` | `['agentWorkload']` | Admin: agent workload (1 min stale) |

---

## API Modules

### `authApi.ts` — API Service Functions

| Function | Method | URL | Description |
|----------|--------|-----|-------------|
| `fetchCsrfToken()` | GET | `/api/accounts/csrf/` | Initialize CSRF cookie |
| `checkSession()` | GET | `/api/accounts/session/` | Check active session |
| `sessionLogin(u, p)` | POST | `/api/accounts/session/login/` | Log in |
| `sessionLogout()` | POST | `/api/accounts/session/logout/` | Log out |
| `register(data)` | POST | `/api/accounts/register/` | Register new customer |
| `getProfile()` | GET | `/api/accounts/profile/` | Get profile |
| `updateProfile(data)` | PATCH | `/api/accounts/profile/update/` | Update profile |
| `changePassword(data)` | POST | `/api/accounts/change-password/` | Change password |
| `getUsers(params)` | GET | `/api/accounts/users/` | List users (admin) |
| `getUserDetail(id)` | GET | `/api/accounts/users/{id}/` | User detail (admin) |
| `updateUserRole(id, role)` | PATCH | `/api/accounts/users/{id}/role/` | Update role (admin) |
| `getAvailableAgents()` | GET | `/api/accounts/agents/available/` | Available agents (admin) |

### `ticketApi.ts` — API Service Functions

| Function | Method | URL | Description |
|----------|--------|-----|-------------|
| `getTickets(params)` | GET | `/api/tickets/` | Paginated ticket list |
| `getTicket(id)` | GET | `/api/tickets/{id}/` | Ticket detail |
| `createTicket(data)` | POST | `/api/tickets/` | Create ticket |
| `updateTicket(id, data)` | PATCH | `/api/tickets/{id}/` | Update ticket |
| `deleteTicket(id)` | DELETE | `/api/tickets/{id}/` | Delete ticket |
| `changeTicketStatus(id, s)` | PATCH | `/api/tickets/{id}/change_status/` | Change status |
| `changeTicketPriority(id, p)` | PATCH | `/api/tickets/{id}/change_priority/` | Change priority |
| `assignTicket(id, agentId)` | PATCH | `/api/tickets/{id}/assign/` | Assign agent |
| `getTicketStatistics()` | GET | `/api/tickets/statistics/` | Statistics |
| `getTicketMessages(ticketId)` | GET | `/api/messages/?ticket={id}` | Messages |
| `addTicketMessage(ticketId, msg)` | POST | `/api/messages/` | Add message |
| `getCategories()` | GET | `/api/categories/` | Categories |
| `createCategory(name)` | POST | `/api/categories/` | Create category |
| `deleteCategory(id)` | DELETE | `/api/categories/{id}/` | Delete category |

### `dashboardApi.ts` — API Service Functions

| Function | Method | URL | Description |
|----------|--------|-----|-------------|
| `getDashboardOverview()` | GET | `/api/dashboard/` | Role-based dashboard |
| `getAgentWorkload()` | GET | `/api/dashboard/agents/` | Agent workload (admin) |

---

## Shared Components

### `Badge.tsx`

Props: `children`, `variant` (`default` | `success` | `warning` | `danger` | `info`), `className`

Helper functions:
- `getStatusBadgeVariant(status)`: OPEN→info, IN_PROGRESS→warning, RESOLVED→success, CLOSED→default
- `getPriorityBadgeVariant(priority)`: LOW→default, MEDIUM→info, HIGH→warning, CRITICAL→danger

### `Button.tsx`

Props: `children`, `variant` (`primary` | `secondary` | `danger` | `success`), `size` (`sm` | `md` | `lg`), `isLoading`, standard button HTML attributes

### `Card.tsx`

Props: `children`, `title`, `className` — renders a white card with optional title.

### `Input.tsx`, `Select.tsx`, `Textarea.tsx`

Standard form components with Tailwind styling and optional `label` prop.

### `Sidebar.tsx`

Navigation sidebar showing:
- User avatar initial + role badge
- Main navigation: Dashboard, All Tickets, Create Ticket
- Admin section (visible to admins only): User Management, Agent Workload, Categories
- Agent quick link: Open Tickets
- Logout button

### `AppLayout.tsx`

Wraps protected routes with `Sidebar` + main content area. Used by `Protected` and `AdminRoute` guards in `App.tsx`.

---

## Role-Specific Pages and Dashboards

### Customer View
- **Dashboard**: Ticket overview (total/open/in-progress/resolved), priority breakdown, customer-specific metrics (open tickets, awaiting response, resolved/closed), recent tickets and messages.
- **Tickets**: Sees only own tickets.
- **Ticket Details**: Can view, can edit only if OPEN, can delete only if OPEN, can reply.

### Agent View
- **Dashboard**: Ticket overview plus agent metrics (assigned to me, unassigned pool, needs attention, status breakdown).
- **Tickets**: Sees assigned tickets + unassigned pool.
- **Ticket Details**: Can change status, change priority, reply. Cannot assign agents or delete.

### Admin View
- **Dashboard**: Full system overview — user counts, global ticket stats, unassigned count, last 7 days activity, tickets by category, messages total.
- **Users**: User management page with search, role filter, and role change.
- **Agent Workload**: Table of all agents with assignment counts by status.
- **Categories**: Create and delete categories.
- **Ticket Details**: All actions — change status, change priority, assign agents, delete tickets.

---

## Loading and Error Handling

### Loading States

Every data-fetching page shows a loading indicator:
- **Tickets page**: `"Loading tickets..."` text
- **Ticket details**: `"Loading ticket..."` then `"Ticket not found."` if null
- **Dashboard**: `"Loading dashboard..."` then `"No data available."` if null
- **Profile**: `"Loading profile..."` then `"Could not load profile."` if null
- **Admin pages**: `"Loading users..."`, `"Loading agent workload..."`, `"Loading categories..."`
- **Auth guards**: Full-screen centered spinner with "Loading..." text
- **Invalid ticket ID**: `"Invalid ticket ID."` with back link

### Error Handling

- **Login/Register errors**: Displayed as red alert banners with server error messages
- **API errors**: Caught by Axios interceptor (401 → redirect, 403 CSRF → retry)
- **Form validation**: Client-side checks (title ≥5 chars, description ≥10 chars) before server submission
- **Profile update**: Mutation-based, cache updated on success
- **Password change**: Inline error/success messages in the profile page

---

## Environment Variables

Frontend environment is configured in `frontend/.env` and `frontend/.env.example`:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_PROXY_TARGET` | `http://localhost:8000` | Backend URL for Vite dev proxy |

**Note**: The `.env` file in the repository contains `VITE_API_URL=/api` which was the old variable name. The proxy target is now configured in `vite.config.ts` as `VITE_API_PROXY_TARGET`.

---

## Vite Proxy Configuration

`frontend/vite.config.ts`

```typescript
const PROXY_TARGET = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: PROXY_TARGET,
        changeOrigin: true,
      },
    },
  },
})
```

The Vite dev server proxies all `/api/*` requests to the Django backend. This means:
- All requests appear same-origin to the browser (localhost:5173), avoiding CORS issues with cookies.
- The Axios `baseURL` is simply `/api` (relative).
- In Docker, `VITE_API_PROXY_TARGET` is set to `http://backend:8000`.

---

## Complete Example: Loading the Ticket List

1. User navigates to `/tickets`.
2. `Protected` guard checks `isAuthenticated` from `AuthContext`.
3. `Tickets.tsx` calls `useTickets({page: 1, status, priority, search})`.
4. `useTickets` calls `ticketApi.getTickets(params)`.
5. `getTickets` calls `axiosClient.get('/tickets/', {params})`.
6. Axios request interceptor reads `csrftoken` cookie and sets `X-CSRFToken` header.
7. Vite proxy forwards to Django (`http://localhost:8000/api/tickets/`).
8. Django authenticates via `sessionid` cookie, filters tickets by user role, returns paginated JSON.
9. Axios response interceptor checks for 401/403.
10. TanStack Query caches the result under `['tickets', params]`.
11. `Tickets.tsx` renders the ticket list with pagination, filters, and search.
12. If the user changes a filter, the query is re-fetched with new params.

---

## Related Documents

- [Architecture](architecture.md) — frontend-to-backend request flow
- [API Reference](api-reference.md) — complete API endpoint documentation
- [Authentication & RBAC](authentication-and-rbac.md) — auth flow details
