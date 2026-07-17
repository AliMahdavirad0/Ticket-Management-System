# Backend

## Technology Stack

- **Django** 6.0.5
- **Django REST Framework** 3.17.1
- **django-filter** 25.2
- **drf-spectacular** 0.29.0
- **django-cors-headers** 4.7.0

## Django Applications and Their Responsibilities

The backend consists of three local apps plus the project configuration app:

### 1. `accounts` — `backend/accounts/`

**Responsibility**: User model, authentication, registration, profile management, and user administration.

| Component | File | Key Classes/Functions |
|-----------|------|-----------------------|
| Models | `backend/accounts/models.py` | `User` (extends `AbstractUser` with `role` field) |
| Session Views | `backend/accounts/session_views.py` | `csrf_token`, `session_check`, `session_login`, `session_logout` |
| Views | `backend/accounts/views.py` | `RegisterView`, `UserProfileView`, `UserUpdateView`, `ChangePasswordView`, `UserListView`, `UserDetailView`, `UserRoleUpdateView`, `available_agents_view` |
| Serializers | `backend/accounts/serializers.py` | `RegisterSerializer`, `UserSerializer`, `UserMinimalSerializer`, `AvailableAgentSerializer`, `UserUpdateSerializer`, `UserRoleUpdateSerializer`, `ChangePasswordSerializer` |
| Permissions | `backend/accounts/permissions.py` | `RolePermission`, `IsAdmin`, `IsAgent`, `IsCustomer`, `IsAgentOrAdmin`, `IsAuthenticatedNonAdmin` |
| Service | `backend/accounts/services/user_service.py` | `UserService` |
| URLs | `backend/accounts/urls.py` | Route definitions |
| Management Command | `backend/accounts/management/commands/seed_data.py` | `Command` — seed demo data |

### 2. `tickets` — `backend/tickets/`

**Responsibility**: Ticket CRUD, status/priority management, ticket messages, categories.

| Component | File | Key Classes/Functions |
|-----------|------|-----------------------|
| Models | `backend/tickets/models.py` | `Ticket`, `TicketCategory`, `TicketMessage` |
| Views | `backend/tickets/views.py` | `TicketViewSet`, `TicketCategoryViewSet`, `TicketMessageViewSet` |
| Serializers | `backend/tickets/serializers.py` | `TicketListSerializer`, `TicketDetailSerializer`, `TicketCreateSerializer`, `TicketUpdateSerializer`, `TicketStatusChangeSerializer`, `TicketAssignSerializer`, `TicketPriorityChangeSerializer`, `TicketCategorySerializer`, `TicketMessageSerializer`, `TicketMessageCreateSerializer` |
| Permissions | `backend/tickets/permissions.py` | `IsTicketOwnerOrAgentOrAdmin`, `CanModifyTicket`, `CanDeleteTicket`, `IsMessageOwnerOrTicketParticipant` |
| Services | `backend/tickets/services/ticket_service.py` | `TicketService` |
| | `backend/tickets/services/message_service.py` | `MessageService` |
| URLs | `backend/tickets/urls.py` | DRF router definitions |

### 3. `dashboard` — `backend/dashboard/`

**Responsibility**: Role-based dashboard overviews and agent workload metrics.

| Component | File | Key Classes/Functions |
|-----------|------|-----------------------|
| Views | `backend/dashboard/views.py` | `DashboardOverviewView`, `AdminAgentWorkloadView` |
| Serializers | `backend/dashboard/serializers.py` | `DashboardOverviewSerializer`, `AgentWorkloadSerializer` |
| Service | `backend/dashboard/services/dashboard_service.py` | `DashboardService` |
| URLs | `backend/dashboard/urls.py` | Route definitions |

### 4. `ticketProject` — `backend/ticketProject/`

**Responsibility**: Project configuration and root URL routing.

| Component | File | Purpose |
|-----------|------|---------|
| Settings | `backend/ticketProject/settings.py` | All Django configuration |
| URL Config | `backend/ticketProject/urls.py` | Root URL routing including admin, API, and docs |
| Exception Handler | `backend/ticketProject/exceptions.py` | `custom_exception_handler` — consistent error responses |
| WSGI | `backend/ticketProject/wsgi.py` | WSGI application |
| ASGI | `backend/ticketProject/asgi.py` | ASGI application |

---

## Service Layer

The service layer encapsulates business logic, keeping views thin and logic testable. All services use `@staticmethod` methods.

### TicketService (`backend/tickets/services/ticket_service.py`)

| Method | Purpose |
|--------|---------|
| `get_tickets_for_user(user)` | Returns QuerySet of tickets filtered by user role with optimized `select_related` and `annotate` |
| `create_ticket(user, validated_data)` | Creates a new ticket for a user |
| `change_ticket_status(ticket, new_status, user)` | Validates status transitions and updates ticket status |
| `assign_agent_to_ticket(ticket, agent_id, user)` | Assigns an agent to a ticket (admin only) |
| `change_ticket_priority(ticket, new_priority, user)` | Changes ticket priority (agent/admin only) |
| `get_ticket_statistics(user)` | Returns role-filtered ticket counts by status and priority |

### MessageService (`backend/tickets/services/message_service.py`)

| Method | Purpose |
|--------|---------|
| `get_messages_for_user(user, ticket_id)` | Returns messages QuerySet filtered by user role and optional ticket |
| `create_message(user, ticket_id, message_content)` | Validates access and creates a message; blocks messages on CLOSED tickets |
| `validate_message_access(user, message)` | Checks if user can access a specific message |

### UserService (`backend/accounts/services/user_service.py`)

| Method | Purpose |
|--------|---------|
| `create_user(username, email, password, role)` | Creates a user with duplicate username/email validation |
| `get_user_profile(user)` | Returns user profile data with role-specific statistics |
| `get_available_agents()` | Returns agents sorted by current workload (assigned open/in-progress tickets) |
| `update_user_role(user_id, new_role, requesting_user)` | Changes a user's role (admin only) |

### DashboardService (`backend/dashboard/services/dashboard_service.py`)

| Method | Purpose |
|--------|---------|
| `get_overview(user)` | Builds dashboard payload with role-specific sections (customer/agent/admin metrics) |
| `get_agent_workload()` | Aggregates agent assignment counts by status |

---

## Serializers

All serializers are in `backend/accounts/serializers.py` and `backend/tickets/serializers.py`.

### Account Serializers

| Serializer | Purpose |
|------------|---------|
| `RegisterSerializer` | User registration — validates password match, enforces customer role |
| `UserSerializer` | Full user info with `statistics` computed field |
| `UserMinimalSerializer` | Lightweight (id, username, email, role, first_name, last_name) — used in nested responses |
| `AvailableAgentSerializer` | Agent list with `assigned_count` |
| `UserUpdateSerializer` | Profile update (email, first_name, last_name) |
| `UserRoleUpdateSerializer` | Role change (choice field) |
| `ChangePasswordSerializer` | Password change with old password validation |

### Ticket Serializers

| Serializer | Purpose |
|------------|---------|
| `TicketListSerializer` | Lightweight list view — truncated description to 200 chars, includes `message_count` |
| `TicketDetailSerializer` | Full detail — includes nested `messages` with sender info |
| `TicketCreateSerializer` | Create — validates title (≥5 chars) and description (≥10 chars) |
| `TicketUpdateSerializer` | Update — same validation as create, but allows partial |
| `TicketStatusChangeSerializer` | Status change — ChoiceField over `Status.choices` |
| `TicketAssignSerializer` | Assignment — accepts `agent_id` IntegerField |
| `TicketPriorityChangeSerializer` | Priority change — ChoiceField over `Priority.choices` |
| `TicketCategorySerializer` | Category — `__all__` fields |
| `TicketMessageSerializer` | Message list — nested sender info via `UserMinimalSerializer` |
| `TicketMessageCreateSerializer` | Message create — validates non-empty message |

---

## Views and ViewSets

### TicketViewSet (`backend/tickets/views.py`)

| Action | Method | URL | Permission |
|--------|--------|-----|------------|
| `list` | GET | `/api/tickets/` | `IsAuthenticated` + `IsTicketOwnerOrAgentOrAdmin` |
| `create` | POST | `/api/tickets/` | `IsAuthenticated` |
| `retrieve` | GET | `/api/tickets/{id}/` | `IsAuthenticated` + `IsTicketOwnerOrAgentOrAdmin` |
| `update` / `partial_update` | PUT/PATCH | `/api/tickets/{id}/` | `IsAuthenticated` + `CanModifyTicket` |
| `destroy` | DELETE | `/api/tickets/{id}/` | `IsAuthenticated` + `CanDeleteTicket` |
| `change_status` | PATCH | `/api/tickets/{id}/change_status/` | `IsAgentOrAdmin` |
| `assign` | PATCH | `/api/tickets/{id}/assign/` | `IsAdmin` |
| `change_priority` | PATCH | `/api/tickets/{id}/change_priority/` | `IsAgentOrAdmin` |
| `statistics` | GET | `/api/tickets/statistics/` | `IsAuthenticated` |

### TicketCategoryViewSet (`backend/tickets/views.py`)

| Action | Permission |
|--------|------------|
| `list`, `retrieve` | `IsAuthenticated` |
| `create`, `update`, `partial_update`, `destroy` | `IsAdmin` |

### TicketMessageViewSet (`backend/tickets/views.py`)

| Action | Permission |
|--------|------------|
| `list`, `create`, `retrieve` | `IsAuthenticated` |
| `update`, `partial_update`, `destroy` | `IsAuthenticated` + `IsMessageOwnerOrTicketParticipant` |

---

## Permission Classes

### Base (`backend/accounts/permissions.py`)

| Class | Allowed Roles |
|-------|---------------|
| `RolePermission` | Base — configurable `allowed_roles` |
| `IsAdmin` | `admin` |
| `IsAgent` | `agent` |
| `IsCustomer` | `customer` |
| `IsAgentOrAdmin` | `agent`, `admin` |
| `IsAuthenticatedNonAdmin` | `customer`, `agent` |

### Ticket Object-Level (`backend/tickets/permissions.py`)

| Class | Logic |
|-------|-------|
| `IsTicketOwnerOrAgentOrAdmin` | Admin: any. Owner: their own. Agent: assigned or unassigned. |
| `CanModifyTicket` | Admin: any. Agent: assigned or unassigned. Customer: own OPEN only. |
| `CanDeleteTicket` | Admin: any. Customer: own OPEN only. Agent: none. |
| `IsMessageOwnerOrTicketParticipant` | Admin: any. Sender: own. Owner: ticket owner. Agent: assigned or unassigned ticket messages. |

---

## URL Routing

### Root (`backend/ticketProject/urls.py`)

```python
path('admin/', admin.site.urls),
path('api/accounts/', include('accounts.urls')),
path('api/dashboard/', include('dashboard.urls')),
path('api/', include('tickets.urls')),
path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
```

### Accounts URLs (`backend/accounts/urls.py`)

```python
# Session authentication
path('csrf/', csrf_token),
path('session/', session_check),
path('session/login/', session_login),
path('session/logout/', session_logout),

# Registration
path('register/', RegisterView.as_view()),

# Profile
path('profile/', UserProfileView.as_view()),
path('profile/update/', UserUpdateView.as_view()),
path('change-password/', ChangePasswordView.as_view()),

# User management (admin only)
path('users/', UserListView.as_view()),
path('users/<int:pk>/', UserDetailView.as_view()),
path('users/<int:pk>/role/', UserRoleUpdateView.as_view()),
path('agents/available/', available_agents_view),
```

### Tickets URLs (`backend/tickets/urls.py`)

Uses `DefaultRouter`:

```
/tickets/          → TicketViewSet
/tickets/{id}/     → TicketViewSet
/categories/       → TicketCategoryViewSet
/categories/{id}/  → TicketCategoryViewSet
/messages/         → TicketMessageViewSet
/messages/{id}/    → TicketMessageViewSet
```

### Dashboard URLs (`backend/dashboard/urls.py`)

```python
path('', DashboardOverviewView.as_view()),
path('agents/', AdminAgentWorkloadView.as_view()),
```

---

## Management Commands

### `seed_data` (`backend/accounts/management/commands/seed_data.py`)

Creates deterministic demo data for development.

**Usage**:
```bash
python manage.py seed_data              # Idempotent seed
python manage.py seed_data --reset       # Delete all data then seed fresh
```

**Creates**:
- 5 users (admin, 2 agents, 2 customers)
- 5 categories
- 15 tickets with various statuses, priorities, and assignments
- Corresponding messages

---

## Django Settings Highlights

Key settings from `backend/ticketProject/settings.py`:

### Authentication
- `AUTH_USER_MODEL = 'accounts.User'` — custom user model
- Session authentication with `SessionAuthentication` as the only auth class
- CSRF with non-HttpOnly cookie (readable by JavaScript)
- `SESSION_COOKIE_HTTPONLY = True` — `sessionid` not readable by JS
- `CSRF_COOKIE_HTTPONLY = False` — `csrftoken` readable by JS

### REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'ticketProject.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}
```

### CORS
- `CORS_ALLOWED_ORIGINS`: `http://localhost:5173`, `http://127.0.0.1:5173`
- `CORS_ALLOW_CREDENTIALS`: `True`

### Security (production, when `DEBUG = False`)
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- `SECURE_HSTS_SECONDS`, `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`
- `X_FRAME_OPTIONS = 'DENY'`

---

## Exception Handling

The custom exception handler at `backend/ticketProject/exceptions.py` normalizes error responses:

| HTTP Status | Response Shape |
|-------------|----------------|
| 400 (Validation) | `{detail: "Validation failed.", errors: {...}}` |
| 401 (Not Authenticated) | Restored from DRF's coerced 403 to proper 401; `{detail, code}` |
| 403 (Permission Denied) | `{detail, code: "permission_denied"}` |
| Other 4xx | `{detail, errors}` |

---

## Related Documents

- [Architecture](architecture.md) — request lifecycle and layering
- [Database](database.md) — data model details
- [API Reference](api-reference.md) — complete endpoint reference
- [Authentication & RBAC](authentication-and-rbac.md) — permissions in detail
