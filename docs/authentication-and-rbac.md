# Authentication and Role-Based Access Control

## Authentication Overview

This project uses **Django Session Authentication** with CSRF protection. There is **no JWT**. Tokens are not stored in `localStorage`. The `sessionid` cookie is `HttpOnly` and cannot be read by JavaScript, providing protection against XSS attacks.

### Why Session Auth?

Session authentication is the natural choice for a server-rendered or SPA application served from the same domain (or via a same-origin proxy). The `sessionid` cookie is automatically sent by the browser, requires no client-side token management, and integrates directly with Django's built-in authentication system.

---

## Authentication Flow

### 1. CSRF Cookie Request

On app mount, the frontend calls `GET /api/accounts/csrf/` to set the `csrftoken` cookie.

```
Frontend → GET /api/accounts/csrf/
Backend  → 200 OK + Set-Cookie: csrftoken=<token>; SameSite=Lax
```

### 2. Session Login

```mermaid
sequenceDiagram
    participant Browser as Browser
    participant LoginView as POST /api/accounts/session/login/
    participant Django as Django Auth
    participant Session as Session Store

    Browser->>LoginView: POST {username, password} + Cookie: csrftoken=... + X-CSRFToken
    LoginView->>Django: authenticate(username, password)
    Django-->>LoginView: User object or None
    Note over LoginView: If successful
    LoginView->>Django: login(request, user)
    Django->>Session: Create session
    Django-->>LoginView: get_token(request) → fresh csrftoken
    LoginView-->>Browser: 200 {user: {...}} + Set-Cookie: sessionid=<hash>; HttpOnly
    Note right of Browser: sessionid is now stored in browser
    Note right of Browser: csrftoken is also refreshed
```

### 3. Authenticated API Requests

On every subsequent request:

1. The browser automatically sends the `sessionid` cookie (HttpOnly, SameSite=Lax).
2. Django's `SessionAuthentication` middleware validates the session.
3. For state-changing requests (POST/PUT/PATCH/DELETE), the Axios request interceptor reads the `csrftoken` cookie and sends it as the `X-CSRFToken` header.

```
GET /api/tickets/
Cookie: sessionid=<hash>
↓
Django validates session → request.user is set
↓
Response with refreshed csrftoken cookie

PATCH /api/tickets/1/
Cookie: sessionid=<hash>
X-CSRFToken: <value from csrftoken cookie>
↓
Django validates session + CSRF token
↓
Business logic executes
```

### 4. Logout

```
POST /api/accounts/session/logout/  (+ X-CSRFToken)
↓
Django: logout(request) → session destroyed
↓
200 OK + sessionid cookie cleared
```

### 5. Session Expiration

- Sessions expire when the browser closes (`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`).
- The Axios response interceptor redirects to `/login` on any `401` response.

---

## CSRF Protection

### Cookie Configuration

| Cookie | `HttpOnly` | `SameSite` | `Secure` (prod) | Purpose |
|--------|-----------|------------|-----------------|---------|
| `sessionid` | `True` | `Lax` | `True` | Session identifier — not readable by JS |
| `csrftoken` | `False` | `Lax` | `True` | CSRF token — readable by JS for header injection |

### Frontend CSRF Handling

The Axios request interceptor (`frontend/src/api/axiosClient.ts`) automatically:

1. Reads the `csrftoken` cookie value via `document.cookie`.
2. Attaches it as the `X-CSRFToken` header on POST/PUT/PATCH/DELETE requests.
3. A response interceptor detects CSRF failures (403 with "CSRF" in detail) and retries once with a fresh token.

### CSRF Trusted Origins

```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',   # Vite dev server
    'http://127.0.0.1:5173',  # Vite dev server (IP)
]
```

In production, `DJANGO_CSRF_TRUSTED_ORIGINS` environment variable is used.

---

## Roles

The system defines three user roles:

| Role | `role` field value | Description |
|------|-------------------|-------------|
| **Customer** | `customer` | End user who creates and tracks support tickets |
| **Agent** | `agent` | Support staff who resolve tickets |
| **Admin** | `admin` | System administrator with full access |

The role is stored as a `CharField` on the `User` model (`backend/accounts/models.py`):

```python
role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
```

---

## Permission Matrix

### Tickets

| Action | Customer | Agent | Admin |
|--------|----------|-------|-------|
| List tickets | Own tickets only | Assigned + unassigned | All |
| View single ticket | Own only | Assigned or unassigned | Any |
| Create ticket | ✅ | ✅ | ✅ |
| Update ticket | Own OPEN only | Assigned or unassigned | Any |
| Delete ticket | Own OPEN only | ❌ | Any |
| Change status | ❌ | ✅ | ✅ |
| Change priority | ❌ | ✅ | ✅ |
| Assign agent | ❌ | ❌ | ✅ |

### Messages

| Action | Customer | Agent | Admin |
|--------|----------|-------|-------|
| List messages | Own tickets | Assigned or unassigned tickets | All |
| Create message | Own tickets only | Assigned tickets or unassigned pool | All |
| Message on CLOSED ticket | ❌ | ❌ | ❌ |
| Modify/delete messages | Own only | Own only (if accessible) | Own only (if accessible) |

### Categories

| Action | Customer | Agent | Admin |
|--------|----------|-------|-------|
| List categories | ✅ | ✅ | ✅ |
| Create/update/delete | ❌ | ❌ | ✅ |

### Users

| Action | Customer | Agent | Admin |
|--------|----------|-------|-------|
| View own profile | ✅ | ✅ | ✅ |
| Update own profile | ✅ | ✅ | ✅ |
| Change own password | ✅ | ✅ | ✅ |
| List all users | ❌ | ❌ | ✅ |
| View user details | ❌ | ❌ | ✅ |
| Change user role | ❌ | ❌ | ✅ |
| View available agents | ❌ | ❌ | ✅ |

### Dashboard

| Action | Customer | Agent | Admin |
|--------|----------|-------|-------|
| View dashboard overview | Own stats | Own + pool stats | Global system stats |
| View agent workload | ❌ | ❌ | ✅ |

---

## Permission Classes

### Role Check Permissions (`backend/accounts/permissions.py`)

| Class | Access |
|-------|--------|
| `IsAdmin` | `role == 'admin'` |
| `IsAgent` | `role == 'agent'` |
| `IsCustomer` | `role == 'customer'` |
| `IsAgentOrAdmin` | `role in ('agent', 'admin')` |
| `IsAuthenticatedNonAdmin` | `role in ('customer', 'agent')` |

### Object-Level Permissions (`backend/tickets/permissions.py`)

#### `IsTicketOwnerOrAgentOrAdmin`
- **Admin**: any ticket
- **Customer**: `ticket.user_id == user.id`
- **Agent**: `ticket.assigned_agent_id == user.id` or `assigned_agent_id is None`
- Used for: `list`, `retrieve`

#### `CanModifyTicket`
- **Admin**: any ticket
- **Customer**: own ticket **and** `ticket.status == 'OPEN'`
- **Agent**: `ticket.assigned_agent_id == user.id` or `assigned_agent_id is None`
- Used for: `update`, `partial_update`

#### `CanDeleteTicket`
- **Admin**: any ticket
- **Customer**: own ticket **and** `ticket.status == 'OPEN'`
- **Agent**: **cannot delete**
- Used for: `destroy`

#### `IsMessageOwnerOrTicketParticipant`
- **Admin**: any message
- **Sender**: `message.sender_id == user.id`
- **Ticket owner**: `message.ticket.user_id == user.id`
- **Agent**: `message.ticket.assigned_agent_id == user.id` or `assigned_agent_id is None`
- Used for: message modify/delete

---

## Service-Layer Validation

In addition to permission classes, the service layer enforces business rules:

### `TicketService.change_ticket_status` (`backend/tickets/services/ticket_service.py`)
- Only agents/admins can change status (`user.role not in ['agent', 'admin'] → PermissionError`).
- Status transition must be valid per the defined transition map.

### `TicketService.assign_agent_to_ticket`
- Only admins can assign agents (`user.role != 'admin' → PermissionError`).
- The agent must exist and have `role == 'agent'`.

### `TicketService.change_ticket_priority`
- Only agents/admins can change priority.

### `MessageService.create_message` (`backend/tickets/services/message_service.py`)
- **Closed ticket check**: No messages allowed on `CLOSED` tickets (any role, including admin).
- **Customer access**: `ticket.user` must be the customer.
- **Agent access**: Must be `ticket.assigned_agent` or ticket must be unassigned.

---

## Authenticated Request Sequence Diagram

Complete flow for an authenticated state-changing request:

```mermaid
sequenceDiagram
    participant Browser as Browser
    participant Axios as Axios Interceptor
    participant CSRF as CSRF Middleware
    participant Auth as Session Middleware
    participant View as View/ViewSet
    participant Perm as Permission Classes
    participant Service as Service Layer
    participant DB as Database

    Browser->>Axios: PATCH /api/tickets/1/change_status/
    Note over Browser,Axios: Cookie: sessionid=<hash>; csrftoken=<token>
    Axios->>Axios: Read csrftoken cookie
    Axios->>Axios: Set X-CSRFToken header
    Axios->>CSRF: Request with Cookie + X-CSRFToken
    CSRF->>CSRF: Validate CSRF token
    CSRF->>Auth: Load session from sessionid cookie
    Auth-->>View: request.user = User(role='agent')
    View->>Perm: has_permission() → IsAgentOrAdmin
    Perm-->>View: True
    View->>Perm: has_object_permission() → (if applicable)
    Perm-->>View: True
    View->>Service: change_ticket_status(ticket, 'IN_PROGRESS', user)
    Service->>Service: Validate transition: OPEN → IN_PROGRESS
    Service->>DB: UPDATE ticket SET status='IN_PROGRESS'
    DB-->>Service: Success
    Service-->>View: Updated Ticket object
    View-->>Browser: 200 + JSON response
```

---

## Registration Role Enforcement

Public registration via `RegisterView` (`backend/accounts/views.py`) only allows the `customer` role:

```python
# backend/accounts/serializers.py
def validate_role(self, value):
    if value and value != 'customer':
        raise serializers.ValidationError(
            'Public registration only allows the customer role.'
        )
    return value or 'customer'
```

The `admin` and `agent` roles can only be assigned by an existing admin via `PATCH /api/accounts/users/{id}/role/`.

---

## Related Documents

- [Architecture](architecture.md) — system architecture overview
- [API Reference](api-reference.md) — endpoint details
- [Backend](backend.md) — permission classes and service layer
- [Frontend](frontend.md) — Axios CSRF handling and auth context
- [Ticket Workflow](ticket-workflow.md) — status transitions and lifecycle
