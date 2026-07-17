# API Reference

## Overview

All API endpoints are prefixed with `/api/`. Authentication is session-based (see [Authentication & RBAC](authentication-and-rbac.md)). The API uses JSON for request and response bodies.

- **Base URL**: `http://localhost:8000/api/`
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Response Format

Successful responses return the expected JSON payload directly.

Error responses use a consistent format (via `backend/ticketProject/exceptions.py`):

```json
{
  "detail": "Error description",
  "code": "error_code",
  "errors": { ... }
}
```

### Pagination

List endpoints use page-based pagination (10 items per page by default):

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/tickets/?page=3",
  "previous": "http://localhost:8000/api/tickets/?page=1",
  "results": [ ... ]
}
```

---

## Authentication Endpoints

### `GET /api/accounts/csrf/`

Set the CSRF cookie.

- **Auth**: None (AllowAny)
- **Response**: `200 OK`
- **Cookies set**: `csrftoken` (readable by JavaScript)

**Example Response:**
```json
{ "detail": "CSRF cookie set." }
```

---

### `GET /api/accounts/session/`

Check if the current session is valid.

- **Auth**: None (AllowAny)
- **Response**: `200 OK` (authenticated) or `401 Unauthorized` (not authenticated)

**Example Response (authenticated):**
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "username": "customer1",
    "email": "cust1@example.com",
    "role": "customer",
    "first_name": "Charlie",
    "last_name": "Brown"
  }
}
```

**Example Response (unauthenticated):**
```json
{ "authenticated": false }
```

---

### `POST /api/accounts/session/login/`

Authenticate with username and password. Creates a Django session.

- **Auth**: None (AllowAny)
- **Cookies set**: `sessionid` (HttpOnly), `csrftoken`

**Request Body:**
```json
{
  "username": "customer1",
  "password": "Cust123!"
}
```

**Example Response (success, `200 OK`):**
```json
{
  "detail": "Login successful.",
  "user": {
    "id": 4,
    "username": "customer1",
    "email": "cust1@example.com",
    "role": "customer",
    "first_name": "Charlie",
    "last_name": "Brown"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account disabled

---

### `POST /api/accounts/session/logout/`

Destroy the current session. Clears cookies.

- **Auth**: Required (IsAuthenticated)

**Example Response (`200 OK`):**
```json
{ "detail": "Logged out successfully." }
```

---

### `POST /api/accounts/register/`

Register a new user account. Only the `customer` role is allowed via public registration.

- **Auth**: None (AllowAny)

**Request Body:**
```json
{
  "username": "newcustomer",
  "email": "new@example.com",
  "password": "SecurePass1!",
  "password2": "SecurePass1!"
}
```

**Example Response (`201 Created`):**
```json
{
  "id": 6,
  "username": "newcustomer",
  "email": "new@example.com",
  "role": "customer"
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors (password mismatch, duplicate username, etc.)

---

## Profile Endpoints

### `GET /api/accounts/profile/`

Get the current user's profile with role-specific statistics.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any

**Example Response (`200 OK` — customer):**
```json
{
  "id": 4,
  "username": "customer1",
  "email": "cust1@example.com",
  "first_name": "Charlie",
  "last_name": "Brown",
  "role": "customer",
  "date_joined": "2025-01-01T00:00:00Z",
  "statistics": {
    "total_tickets": 5,
    "open_tickets": 2,
    "resolved_tickets": 1
  }
}
```

**Example Response (`200 OK` — agent):**
```json
{
  "id": 2,
  "username": "agent1",
  "role": "agent",
  "statistics": {
    "assigned_tickets": 3,
    "open_assigned": 1,
    "resolved_assigned": 1
  }
}
```

---

### `PATCH /api/accounts/profile/update/`

Update the current user's profile fields.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any

**Request Body:**
```json
{
  "first_name": "NewFirst",
  "last_name": "NewLast",
  "email": "newemail@example.com"
}
```

**Example Response (`200 OK`):**
```json
{
  "email": "newemail@example.com",
  "first_name": "NewFirst",
  "last_name": "NewLast"
}
```

---

### `POST /api/accounts/change-password/`

Change the current user's password.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password2": "NewPass456!"
}
```

**Example Response (`200 OK`):**
```json
{ "message": "Password changed successfully" }
```

**Error Responses:**
- `400 Bad Request`: Wrong old password, passwords don't match, or validation errors

---

## User Management Endpoints (Admin)

### `GET /api/accounts/users/`

List all users with optional filtering. Paginated (10 per page).

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number |
| `role` | string | Filter by role: `customer`, `agent`, `admin` |
| `search` | string | Search by username, email, first name, or last name |

**Example Response (`200 OK`):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin1",
      "email": "admin@example.com",
      "role": "admin",
      "first_name": "",
      "last_name": "",
      "date_joined": "2025-01-01T00:00:00Z",
      "statistics": {}
    }
  ]
}
```

---

### `GET /api/accounts/users/{id}/`

Get a single user's details.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Example Response (`200 OK`):** Same structure as user list item.

---

### `PATCH /api/accounts/users/{id}/role/`

Update a user's role.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Request Body:**
```json
{
  "role": "agent"
}
```

**Example Response (`200 OK`):**
```json
{
  "message": "User role updated successfully",
  "user": {
    "id": 4,
    "username": "customer1",
    "email": "cust1@example.com",
    "role": "agent",
    "first_name": "Charlie",
    "last_name": "Brown"
  }
}
```

**Error Responses:**
- `403 Forbidden`: Non-admin user attempting this action
- `400 Bad Request`: Invalid role or non-existent user

---

### `GET /api/accounts/agents/available/`

Get agents sorted by current workload (ascending assigned open/in-progress tickets).

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Example Response (`200 OK`):**
```json
[
  {
    "id": 3,
    "username": "agent2",
    "email": "agent2@example.com",
    "first_name": "Bob",
    "last_name": "Jones",
    "assigned_count": 1
  },
  {
    "id": 2,
    "username": "agent1",
    "email": "agent1@example.com",
    "first_name": "Alice",
    "last_name": "Smith",
    "assigned_count": 3
  }
]
```

---

## Ticket Endpoints

### `GET /api/tickets/`

List tickets. Results are filtered by user role (customers see their own, agents see assigned + unassigned, admins see all). Paginated (10 per page).

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number |
| `status` | string | Filter by status: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `priority` | string | Filter by priority: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `category` | int | Filter by category ID |
| `assigned_agent` | int | Filter by assigned agent ID |
| `search` | string | Search in title and description |
| `ordering` | string | `created_at`, `-created_at`, `updated_at`, `-updated_at`, `priority`, `-priority` |

**Example Response (`200 OK`):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/tickets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Issue #1: Login Support Error",
      "description": "Detailed description for ticket...",
      "status": "OPEN",
      "priority": "HIGH",
      "user": { "id": 4, "username": "customer1", "email": "cust1@example.com" },
      "assigned_agent": null,
      "category": { "id": 1, "name": "Technical Support" },
      "message_count": 1,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

### `POST /api/tickets/`

Create a new ticket. The authenticated user becomes the ticket owner.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user

**Request Body:**
```json
{
  "title": "Cannot access my account",
  "description": "I have been unable to log in since the last update. The login page shows an error.",
  "priority": "HIGH",
  "category": 1
}
```

**Validation Rules:**
- `title`: minimum 5 characters
- `description`: minimum 10 characters

**Example Response (`201 Created`):** Same as `GET /api/tickets/{id}/` detail response.

**Error Responses:**
- `400 Bad Request`: Validation errors (title too short, description too short)

---

### `GET /api/tickets/{id}/`

Get a single ticket with full details, including all messages.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Owner, assigned agent/unassigned pool (agent), or admin

**Example Response (`200 OK`):**
```json
{
  "id": 1,
  "title": "Issue #1: Login Support Error",
  "description": "Detailed description for ticket #1...",
  "status": "OPEN",
  "priority": "HIGH",
  "user": { "id": 4, "username": "customer1", "email": "cust1@example.com", "role": "customer" },
  "assigned_agent": null,
  "category": { "id": 1, "name": "Technical Support" },
  "messages": [
    {
      "id": 1,
      "ticket": 1,
      "sender": { "id": 4, "username": "customer1", "email": "cust1@example.com", "role": "customer" },
      "message": "I am reporting this issue.",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

**Error Responses:**
- `403 Forbidden`: User does not have access to this ticket

---

### `PATCH /api/tickets/{id}/`

Update a ticket's title, description, priority, or category.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Owner (only if OPEN), assigned agent/unassigned pool (agent), or admin

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description for the issue"
}
```

**Validation Rules:**
- `title`: minimum 5 characters (if provided)
- `description`: minimum 10 characters (if provided)

**Example Response (`200 OK`):** Full ticket detail.

---

### `DELETE /api/tickets/{id}/`

Delete a ticket.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin (any ticket) or customer (own OPEN tickets only). Agents cannot delete.

**Example Response (`204 No Content`).**

---

### `PATCH /api/tickets/{id}/change_status/`

Change the status of a ticket.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Agent or Admin

**Request Body:**
```json
{
  "status": "IN_PROGRESS"
}
```

**Valid Transitions:**
| Current | Allowed Next |
|---------|--------------|
| OPEN | `IN_PROGRESS`, `CLOSED` |
| IN_PROGRESS | `RESOLVED`, `CLOSED` |
| RESOLVED | `IN_PROGRESS`, `CLOSED` |
| CLOSED | `OPEN` (admin only) |

**Example Response (`200 OK`):** Full ticket detail with updated status.

**Error Responses:**
- `400 Bad Request`: Invalid status or invalid transition
- `403 Forbidden`: Customer attempting to change status

---

### `PATCH /api/tickets/{id}/assign/`

Assign an agent to a ticket.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Request Body:**
```json
{
  "agent_id": 2
}
```

**Example Response (`200 OK`):**
```json
{
  "message": "Agent assigned successfully",
  "agent": "agent1",
  "ticket": { ... full ticket detail ... }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid agent ID or user is not an agent
- `403 Forbidden`: Non-admin user attempting to assign

---

### `PATCH /api/tickets/{id}/change_priority/`

Change the priority of a ticket.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Agent or Admin

**Request Body:**
```json
{
  "priority": "CRITICAL"
}
```

**Example Response (`200 OK`):** Full ticket detail with updated priority.

---

### `GET /api/tickets/statistics/`

Get ticket statistics for the current user (role-filtered).

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user

**Example Response (`200 OK`):**
```json
{
  "total": 10,
  "open": 3,
  "in_progress": 2,
  "resolved": 3,
  "closed": 2,
  "by_priority": {
    "low": 2,
    "medium": 3,
    "high": 3,
    "critical": 2
  }
}
```

---

## Ticket Message Endpoints

### `GET /api/messages/`

List messages. Can be filtered by ticket ID.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user (filtered by role)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Filter by ticket ID |

**Example Response (`200 OK`):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "ticket": 1,
      "sender": { "id": 4, "username": "customer1", "email": "cust1@example.com", "role": "customer" },
      "message": "I am reporting this issue.",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

### `POST /api/messages/`

Create a new message on a ticket.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user (with access to the ticket)

**Request Body:**
```json
{
  "ticket": 1,
  "message": "I'm still having this issue. Can you please look into it?"
}
```

**Validation Rules:**
- `message`: cannot be empty
- Cannot message on a `CLOSED` ticket (any role, including admin)
- Customers: only on own tickets
- Agents: only on assigned tickets or unassigned pool tickets

**Example Response (`201 Created`):**
```json
{
  "id": 6,
  "ticket": 1,
  "sender": { "id": 4, "username": "customer1", "email": "cust1@example.com", "role": "customer" },
  "message": "I'm still having this issue.",
  "created_at": "2025-01-15T12:00:00Z"
}
```

**Error Responses:**
- `403 Forbidden`: Cannot message on a closed ticket, or no access to this ticket
- `400 Bad Request`: Ticket does not exist

---

## Category Endpoints

### `GET /api/categories/`

List all categories. Paginated.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user

**Example Response (`200 OK`):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "name": "Technical Support" },
    { "id": 2, "name": "Billing" }
  ]
}
```

---

### `POST /api/categories/`

Create a new category.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Request Body:**
```json
{
  "name": "New Category"
}
```

**Example Response (`201 Created`):**
```json
{ "id": 6, "name": "New Category" }
```

---

### `DELETE /api/categories/{id}/`

Delete a category. Tickets in this category will have `category` set to `NULL`.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Example Response (`204 No Content`).**

---

## Dashboard Endpoints

### `GET /api/dashboard/`

Get a role-based dashboard overview.

- **Auth**: Required (IsAuthenticated)
- **Roles**: Any authenticated user

**Response sections vary by role:**

**Customer overview** includes: `user`, `tickets` (stats), `messages`, `recent_tickets`, `recent_messages`, `customer` (open_tickets, awaiting_response, resolved_or_closed).

**Agent overview** includes: `user`, `tickets` (stats), `messages`, `recent_tickets`, `recent_messages`, `agent` (assigned_to_me, unassigned_pool, needs_attention, by_status).

**Admin overview** includes: `user`, `tickets` (stats), `messages`, `recent_tickets`, `recent_messages`, `admin` (users stats, global ticket stats, by_category, messages total).

**Example Response (`200 OK` — customer):**
```json
{
  "user": { "id": 4, "username": "customer1", "email": "cust1@example.com", "role": "customer" },
  "tickets": {
    "total": 5,
    "open": 2,
    "in_progress": 1,
    "resolved": 1,
    "closed": 1,
    "by_priority": { "low": 1, "medium": 2, "high": 1, "critical": 1 }
  },
  "messages": { "total": 8 },
  "recent_tickets": [ ... ],
  "recent_messages": [ ... ],
  "customer": { "open_tickets": 2, "awaiting_response": 3, "resolved_or_closed": 2 }
}
```

---

### `GET /api/dashboard/agents/`

Get agent workload breakdown (admin only).

- **Auth**: Required (IsAuthenticated)
- **Roles**: Admin only

**Example Response (`200 OK`):**
```json
[
  {
    "id": 2,
    "username": "agent1",
    "email": "agent1@example.com",
    "assigned_total": 5,
    "open": 2,
    "in_progress": 1,
    "resolved": 1,
    "closed": 1
  },
  {
    "id": 3,
    "username": "agent2",
    "email": "agent2@example.com",
    "assigned_total": 3,
    "open": 1,
    "in_progress": 1,
    "resolved": 0,
    "closed": 1
  }
]
```

---

## Error Codes Reference

| HTTP Status | Common Causes |
|-------------|---------------|
| `400 Bad Request` | Validation errors, invalid transitions, missing fields |
| `401 Unauthorized` | No session or expired session |
| `403 Forbidden` | Insufficient role, no object permission, closed ticket messaging |
| `404 Not Found` | Resource does not exist |
| `204 No Content` | Successful deletion |

---

## Related Documents

- [Authentication & RBAC](authentication-and-rbac.md) — auth flow, CSRF, role definitions
- [Ticket Workflow](ticket-workflow.md) — status transitions and lifecycle rules
- [Backend](backend.md) — views, serializers, and services that implement these endpoints
