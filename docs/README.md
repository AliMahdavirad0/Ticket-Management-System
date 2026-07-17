# Documentation Index

> A full-stack role-based ticket management system with session authentication.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0, Django REST Framework 3.17, Session Authentication |
| **Frontend** | React 18, TypeScript, TanStack Query 5, Tailwind CSS 3, Vite 5 |
| **Database** | SQLite (development); PostgreSQL recommended for production |
| **API Docs** | drf-spectacular (Swagger UI / ReDoc) |
| **Containerization** | Docker Compose |
| **CI/CD** | GitHub Actions |

## Documentation Navigation

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | High-level system architecture, backend layering, request lifecycle |
| [C4 Model](c4-model.md) | C4 context/container/component diagrams and dynamic flows |
| [Backend](backend.md) | Django applications, services, serializers, views, permissions |
| [Frontend](frontend.md) | React structure, routing, API clients, hooks, components |
| [Database](database.md) | Data models, fields, relationships, ER diagram |
| [API Reference](api-reference.md) | Complete endpoint reference with request/response examples |
| [Authentication & RBAC](authentication-and-rbac.md) | Session auth flow, CSRF, roles, permission matrix |
| [Ticket Workflow](ticket-workflow.md) | Status transitions, role-based rules, lifecycle |
| [Setup & Development](setup-and-development.md) | Quick start, manual setup, environment variables |
| [Testing](testing.md) | Test structure, running tests, CI execution |
| [Deployment](deployment.md) | Current Docker setup, production recommendations |
| [Limitations & Roadmap](limitations-and-roadmap.md) | Current limitations, prioritized roadmap |

## Recommended Reading Order

1. [Architecture](architecture.md) — understand the system before diving into details
2. [C4 Model](c4-model.md) — visual overview of components and interactions
3. [Authentication & RBAC](authentication-and-rbac.md) — core security concepts
4. [Backend](backend.md) or [Frontend](frontend.md) — depending on your focus
5. [Database](database.md) — data model reference
6. [API Reference](api-reference.md) — when building integrations
7. [Ticket Workflow](ticket-workflow.md) — business logic details
8. [Setup & Development](setup-and-development.md) — to run the project
9. [Testing](testing.md) — for contributor guidance
10. [Deployment](deployment.md) — for production planning
11. [Limitations & Roadmap](limitations-and-roadmap.md) — future direction

## Links

- [Root README](../README.md) — project overview, quick start, demo credentials

---

Return to [Root README](../README.md).
