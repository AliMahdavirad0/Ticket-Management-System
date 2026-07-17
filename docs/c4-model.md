# C4 Model

## Introduction

This document describes the Ticket Management System using the **C4 model** for visualizing software architecture. Diagrams follow the C4 hierarchical approach:

1. **System Context** — the system and its users
2. **Container** — the high-level technical containers
3. **Component** — the major structural components inside each container

All diagram details are verified against the actual source code in this repository. Terminology is consistent with the [Architecture](architecture.md) and other documentation pages.

### Scope

The system is a **role-based ticket management application** with three user roles (Customer, Agent, Admin) that allows ticket creation, assignment, status tracking, and messaging.

### Assumptions and Constraints

- The application runs in a local development or single-server environment.
- SQLite is the database; no external database server is required.
- Session authentication requires browser cookie support; no JWT.
- No email, file upload, or real-time services are integrated.

---

## A. System Context Diagram

```mermaid
flowchart TD
    subgraph "Users"
        Customer["Customer\n[Person]\nReports and tracks\nsupport tickets"]
        Agent["Agent\n[Person]\nHandles assigned tickets\nand resolves issues"]
        Admin["Admin\n[Person]\nManages users, agents,\ncategories, and system"]
    end

    subgraph "System"
        TMS["Ticket Management System\n[Software System]\nFull-stack web application\nfor ticket management\nwith role-based access"]
    end

    Customer -->|"Creates and views tickets\nsends messages"| TMS
    Agent -->|"Manages assigned tickets\nchanges status/priority\nreplies to customers"| TMS
    Admin -->|"Manages users, roles,\ncategories, agent workload\nsystem-wide metrics"| TMS
```

### Explanation

- **Customer**: Creates support tickets, views their own tickets, sends and receives messages. Can only see their own tickets.
- **Agent**: Views assigned and unassigned tickets, changes status and priority, replies to customer messages. Cannot see tickets assigned to other agents.
- **Admin**: Full access to all tickets, users, categories, and agent workload data. Manages role assignments and system configuration.
- **Ticket Management System**: The software system that provides all these capabilities through a web browser interface.

---

## B. Container Diagram

```mermaid
flowchart TD
    subgraph "Users"
        Actor["User (Browser)"]
    end

    subgraph "Ticket Management System"
        Frontend["React Frontend\n[Container: JavaScript/TypeScript]\nSPA with Vite dev server\nPort 5173"]
        
        Backend["Django REST API\n[Container: Python/Django]\nDRF API with session auth\nPort 8000"]

        DB[(SQLite Database\n[Container: SQLite]\nFile-based database\nbackend/db.sqlite3)]

        APIDocs["Swagger UI / ReDoc\n[Container: drf-spectacular]\nInteractive API docs\n/api/docs/ | /api/redoc/"]
    end

    Actor -->|"HTTP :5173"| Frontend
    Frontend -->|"HTTP /api/* proxy"| Backend
    Backend -->|"Django ORM"| DB
    Backend -->|"Serve OpenAPI schema"| APIDocs

    style Actor fill:#e1f5fe,stroke:#01579b
    style Frontend fill:#f3e5f5,stroke:#7b1fa2
    style Backend fill:#fff3e0,stroke:#e65100
    style DB fill:#e8f5e9,stroke:#1b5e20
    style APIDocs fill:#fce4ec,stroke:#c62828
```

### Container Responsibilities

| Container | Technology | Responsibility |
|-----------|-----------|----------------|
| **React Frontend** | React 18, TypeScript, Vite 5, TanStack Query 5, Tailwind CSS 3 | Single-page application providing the user interface. Routes, manages auth state, calls the API via Axios. |
| **Django REST API** | Django 6.0, DRF 3.17, Session Authentication | HTTP API server handling all business logic. Uses a View → Service → Model layered architecture. |
| **SQLite Database** | SQLite (via Django ORM) | Persistent storage for users, tickets, messages, and categories. File-based, no separate server. |
| **Swagger UI / ReDoc** | drf-spectacular 0.29.0 | Generated API documentation served by Django. Schema at `/api/schema/`, UI at `/api/docs/` and `/api/redoc/`. |

Docker Compose orchestrates the frontend and backend containers for local development (`backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`).

---

## C. Component Diagram — Backend

```mermaid
flowchart TD
    subgraph "Django REST API"
        subgraph "accounts App [backend/accounts/]"
            AccountViews["views.py\nRegisterView\nUserProfileView\nUserListView\nUserRoleUpdateView\nChangePasswordView"]
            SessionViews["session_views.py\ncsrf_token\nsession_check\nsession_login\nsession_logout"]
            AccountSerializers["serializers.py\nRegisterSerializer\nUserSerializer\nUserMinimalSerializer\nAvailableAgentSerializer"]
            AccountPermissions["permissions.py\nIsAdmin | IsAgent\nIsCustomer | IsAgentOrAdmin\nRolePermission"]
            UserService["services/user_service.py\nUserService\ncreate_user\nget_user_profile\nget_available_agents\nupdate_user_role"]
        end

        subgraph "tickets App [backend/tickets/]"
            TicketViews["views.py\nTicketViewSet\nTicketCategoryViewSet\nTicketMessageViewSet"]
            TicketSerializers["serializers.py\nTicketListSerializer\nTicketDetailSerializer\nTicketCreateSerializer\nTicketStatusChangeSerializer\nTicketAssignSerializer"]
            TicketPermissions["permissions.py\nIsTicketOwnerOrAgentOrAdmin\nCanModifyTicket\nCanDeleteTicket\nIsMessageOwnerOrTicketParticipant"]
            TicketService["services/ticket_service.py\nTicketService\nget_tickets_for_user\ncreate_ticket\nchange_ticket_status\nassign_agent_to_ticket\nchange_ticket_priority\nget_ticket_statistics"]
            MessageService["services/message_service.py\nMessageService\nget_messages_for_user\ncreate_message\nvalidate_message_access"]
        end

        subgraph "dashboard App [backend/dashboard/]"
            DashboardViews["views.py\nDashboardOverviewView\nAdminAgentWorkloadView"]
            DashboardSerializers["serializers.py\nDashboardOverviewSerializer\nAgentWorkloadSerializer"]
            DashboardService["services/dashboard_service.py\nDashboardService\nget_overview\nget_agent_workload"]
        end

        subgraph "Core Configuration [backend/ticketProject/]"
            Urls["urls.py\nRoot URL routing"]
            Settings["settings.py\nDjango configuration"]
            Exceptions["exceptions.py\nCustom exception handler"]
        end
    end

    Urls --> AccountViews
    Urls --> SessionViews
    Urls --> TicketViews
    Urls --> DashboardViews

    TicketViews --> TicketService
    TicketViews --> MessageService
    TicketViews --> TicketPermissions
    TicketViews --> AccountPermissions
    TicketViews --> TicketSerializers

    AccountViews --> UserService
    AccountViews --> AccountPermissions

    DashboardViews --> DashboardService
    DashboardService --> TicketService
    DashboardService --> MessageService

    TicketService --> TicketSerializers
```

### View → Service → Model Flow

- **TicketViewSet** delegates business logic to `TicketService` and `MessageService`.
- **User views** delegate to `UserService`.
- **Dashboard views** delegate to `DashboardService`, which internally uses `TicketService` and `MessageService` for data aggregation.
- Services interact directly with Django models (ORM) and return results to views, which then pass data through serializers for the HTTP response.

---

## D. Component Diagram — Frontend

```mermaid
flowchart TD
    subgraph "React Frontend [frontend/src/]"
        subgraph "Pages [pages/]"
            Login["Login.tsx"]
            Register["Register.tsx"]
            Dashboard["Dashboard.tsx"]
            Tickets["Tickets.tsx"]
            TicketDetails["TicketDetails.tsx"]
            CreateTicket["CreateTicket.tsx"]
            Profile["Profile.tsx"]
            AdminUsers["AdminUsers.tsx"]
            AdminAgentWorkload["AdminAgentWorkload.tsx"]
            AdminCategories["AdminCategories.tsx"]
            NotFound["NotFound.tsx"]
        end

        subgraph "API Layer [api/]"
            AxiosClient["axiosClient.ts\nAxios config\nCSRF interceptor\nRetry logic"]
            AuthAPI["authApi.ts\nAuth, profile,\nuser management calls"]
            TicketAPI["ticketApi.ts\nTicket CRUD, messages,\ncategories calls"]
            DashboardAPI["dashboardApi.ts\nDashboard calls"]
        end

        subgraph "Hooks [hooks/]"
            UseAuth["useAuth.ts\nTanStack Query hooks\nfor auth/profile/users"]
            UseTickets["useTickets.ts\nTanStack Query hooks\nfor tickets/messages/categories"]
            UseDashboard["useDashboard.ts\nTanStack Query hooks\nfor dashboard"]
        end

        subgraph "Context [context/]"
            AuthContext["AuthContext.tsx\nAuth state management\nLogin/logout/refresh\nSession check on mount"]
        end

        subgraph "Components [components/]"
            AppLayout["AppLayout.tsx"]
            Sidebar["Sidebar.tsx"]
            Badge["Badge.tsx"]
            Button["Button.tsx"]
            Card["Card.tsx"]
            Input["Input.tsx"]
            Select["Select.tsx"]
            Textarea["Textarea.tsx"]
        end

        App["App.tsx\nRouting & auth guards"]
        Main["main.tsx\nReact entry point\nQueryClient + BrowserRouter"]
    end

    Main --> App
    App --> Pages
    App --> AuthContext
    Pages --> Hooks
    Pages --> Components
    Hooks --> API
    API --> AxiosClient
    Sidebar --> AuthContext
    Sidebar --> UseAuth
```

### Frontend Communication with Backend

1. **AxiosClient** (`frontend/src/api/axiosClient.ts`) creates an Axios instance with `baseURL: '/api'` and `withCredentials: true`.
2. The **request interceptor** reads the `csrftoken` cookie and adds `X-CSRFToken` header on POST/PUT/PATCH/DELETE.
3. The **response interceptor** handles 401 (session expired → redirect to `/login`) and 403 CSRF errors (retry once with fresh token).
4. The **AuthContext** (`frontend/src/context/AuthContext.tsx`) calls `/api/accounts/csrf/` on mount, then checks the session via `/api/accounts/session/`.
5. All API calls go through Vite's proxy (`frontend/vite.config.ts`), forwarding `/api/*` to the Django backend.

---

## E. Dynamic Flow — User Login

```mermaid
sequenceDiagram
    participant User as User
    participant LoginPage as Login.tsx
    participant Axios as axiosClient.ts
    participant CsrfView as csrf_token (session_views.py)
    participant SessionView as session_check (session_views.py)
    participant LoginView as session_login (session_views.py)
    participant AuthContext as AuthContext.tsx

    Note over User,AuthContext: On app mount (AuthProvider useEffect)
    User->>LoginPage: Open /login
    Axios->>CsrfView: GET /api/accounts/csrf/
    CsrfView-->>Axios: 200 + Set-Cookie: csrftoken=...
    Axios->>SessionView: GET /api/accounts/session/
    SessionView-->>Axios: 401 {authenticated: false}

    Note over User,AuthContext: No active session → show login form

    User->>LoginPage: Enter username + password, click Login
    LoginPage->>AuthContext: login(username, password)
    AuthContext->>Axios: POST /api/accounts/session/login/
    Axios->>Axios: Read csrftoken cookie\nAttach X-CSRFToken header
    Axios->>LoginView: POST {username, password}
    LoginView->>LoginView: authenticate() → login() + get_token()
    LoginView-->>Axios: 200 {user: {...}} + Set-Cookie: sessionid=...
    Axios-->>AuthContext: {user: {...}}
    AuthContext->>AuthContext: setState(isAuthenticated: true, user)
    AuthContext->>LoginPage: Navigate to /dashboard
```

## F. Dynamic Flow — Ticket Creation and Reply

```mermaid
sequenceDiagram
    participant User as Customer
    participant CTicket as CreateTicket.tsx
    participant TicketDetail as TicketDetails.tsx
    participant Axios as axiosClient.ts
    participant TicketView as TicketViewSet (views.py)
    participant TService as TicketService
    participant MService as MessageService
    participant DB as SQLite

    User->>CTicket: Fill title, description, priority, category
    User->>CTicket: Click "Create Ticket"
    CTicket->>Axios: POST /api/tickets/ + X-CSRFToken
    Axios->>TicketView: TicketViewSet.create()
    TicketView->>TService: create_ticket(user, validated_data)
    TService->>DB: INSERT ticket
    TService-->>TicketView: Ticket instance
    TicketView-->>Axios: 201 TicketDetail JSON
    Axios-->>CTicket: Ticket created
    CTicket-->>User: Navigate to /tickets/{id}

    Note over User,DB: Agent later views and replies

    User->>TicketDetail: View ticket detail
    TicketDetail->>Axios: GET /api/tickets/{id}/
    Axios->>TicketView: TicketViewSet.retrieve()
    TicketView-->>Axios: 200 TicketDetail + messages
    Axios-->>TicketDetail: {ticket, messages}
    
    User->>TicketDetail: Type reply, click "Send Reply"
    TicketDetail->>Axios: POST /api/messages/ + X-CSRFToken
    Axios->>MView: TicketMessageViewSet.create()
    MView->>MService: create_message(user, ticket_id, message)
    MService->>MService: Validate access + closed ticket check
    MService->>DB: INSERT message + UPDATE ticket updated_at
    MService-->>MView: TicketMessage instance
    MView-->>Axios: 201 TicketMessage JSON
    Axios-->>TicketDetail: Message added
```

---

## Related Documents

- [Architecture](architecture.md) — detailed system architecture
- [Backend](backend.md) — backend component reference
- [Frontend](frontend.md) — frontend component reference
- [Authentication & RBAC](authentication-and-rbac.md) — authentication flow details
- [Ticket Workflow](ticket-workflow.md) — ticket lifecycle
