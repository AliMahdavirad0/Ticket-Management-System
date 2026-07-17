# Limitations and Roadmap

## Current Limitations

These limitations are verified in the current implementation.

### 1. SQLite Database

The project uses SQLite (`django.db.backends.sqlite3`), which is suitable for development and small-scale use but has limitations for production:
- No concurrent write support (single-writer lock)
- Limited to a single server (not suitable for horizontal scaling)
- No built-in replication or failover
- Performance degrades with many concurrent users

**Migration path**: PostgreSQL (see [Deployment](deployment.md)).

### 2. No Email Notifications

The system does not send any email notifications. Users are not notified when:
- A ticket is created
- A ticket is assigned to an agent
- A ticket status changes
- A new message is posted
- A ticket is resolved or closed

Users must manually check the dashboard for updates.

### 3. No File Attachments

Tickets and messages cannot include file attachments. The `Ticket` and `TicketMessage` models have no file or image fields. The only content is text-based (`description` and `message` fields).

### 4. No Real-Time Updates

The frontend polls the API using TanStack Query's `staleTime` configuration (ranging from 30 seconds for tickets to 5 minutes for categories). There is no WebSocket, Server-Sent Events (SSE), or long-polling mechanism. Users must refresh or wait for the next automatic refetch to see changes made by others.

### 5. No Rate Limiting

There is no rate limiting configured. Django REST Framework's `DEFAULT_THROTTLE_CLASSES` and `DEFAULT_THROTTLE_RATES` are not set. A malicious user could make unlimited requests.

### 6. Session Authentication for API-Only or Mobile Clients

Session authentication requires cookie support. This means:
- Mobile apps or non-browser clients cannot easily authenticate without a proxy that handles cookies.
- There is no token-based auth (no JWT, no API keys).
- The `sessionid` cookie is `SESSION_COOKIE_SAMESITE = 'Lax'`, which limits cross-origin requests.

### 7. No Frontend Tests

The frontend has no automated tests:
- No unit tests for components, hooks, or API services
- No integration tests
- No end-to-end tests
- TypeScript type checking (`tsc --noEmit`) is the only frontend validation

### 8. No Audit Logging

There is no audit log tracking who performed which action and when. While Django admin logs are available for admin actions, the API does not record changes to tickets, status transitions, or role changes in a structured audit trail.

### 9. Limited Search

The search functionality uses Django ORM's `icontains` lookups on title and description (`SearchFilter`). There is no full-text search engine (like Elasticsearch, Whoosh, or PostgreSQL full-text search). Search performance will degrade as the database grows.

### 10. No Observability

- No structured logging for production (JSON log format)
- No metrics collection (request latency, error rates, throughput)
- No distributed tracing
- No application performance monitoring (APM) integration

### 11. Development Server in Docker

The Docker Compose setup uses `manage.py runserver` for the backend and `npm run dev` for the frontend — both are development servers, not suitable for production.

---

## Roadmap

> The following items are **proposals** for future development. They are not existing features or commitments.

### Phase 1: Production Readiness (High Priority)

| Item | Description | Effort |
|------|-------------|--------|
| PostgreSQL Migration | Replace SQLite with PostgreSQL | Medium |
| Gunicorn + Nginx | Replace Django dev server with Gunicorn; add Nginx reverse proxy | Medium |
| Production Docker Compose | Create production Docker Compose file with Gunicorn, Nginx, PostgreSQL | Medium |
| Secret Management | Proper secret key management for production | Low |
| Environment Configuration | Comprehensive environment variable configuration for production | Low |
| Health Check Endpoint | Dedicated `/api/health/` endpoint with DB connectivity check | Low |

### Phase 2: Notifications (High Priority)

| Item | Description | Effort |
|------|-------------|--------|
| Email Notifications | Send emails on ticket creation, status change, message reply | Medium |
| Email Templates | Role-specific email templates for different events | Medium |

### Phase 3: Attachments (Medium Priority)

| Item | Description | Effort |
|------|-------------|--------|
| File Upload Support | Add file attachment fields to Ticket and TicketMessage models | Medium |
| Media Storage | Configure media file storage (local or S3-compatible) | Low |
| File Validation | File type, size validation, and anti-virus scanning | Low |

### Phase 4: Real-Time Updates (Medium Priority)

| Item | Description | Effort |
|------|-------------|--------|
| WebSocket Support | Add Django Channels for WebSocket connections | High |
| Live Notifications | Real-time updates for new messages and status changes | Medium |
| Presence Indicators | Show which agents are online | Medium |

### Phase 5: Observability (Medium Priority)

| Item | Description | Effort |
|------|-------------|--------|
| Structured Logging | JSON-format logging for production | Low |
| APM Integration | Sentry, New Relic, or DataDog integration | Low |
| Metrics | Prometheus metrics for request rates, latencies, error rates | Medium |
| Dashboard | Grafana dashboard for system monitoring | Medium |

### Phase 6: Quality and Security (Medium Priority)

| Item | Description | Effort |
|------|-------------|--------|
| Rate Limiting | Configure DRF throttling for API endpoints | Low |
| Audit Log | Track all state changes with actor, timestamp, old/new values | Medium |
| Frontend Tests | Unit tests for React components and hooks | Medium |
| E2E Tests | Cypress or Playwright end-to-end tests | High |
| API Tests | Comprehensive API integration tests | Medium |
| Search Improvements | PostgreSQL full-text search or Elasticsearch | Medium |

### Phase 7: Automation (Low Priority)

| Item | Description | Effort |
|------|-------------|--------|
| CI/CD Pipeline | Automated deployment pipeline (build → test → deploy) | Medium |
| Database Migration Automation | Zero-downtime migration strategy | Medium |
| Backup Automation | Automated database backups with retention policy | Low |
| Infrastructure as Code | Terraform or Pulumi for cloud infrastructure | High |

### Phase 8: Advanced Features (Low Priority)

| Item | Description | Effort |
|------|-------------|--------|
| SLA Tracking | Track response time, resolution time per ticket | Medium |
| API Token Auth | Add token/JWT auth for API clients and mobile apps | Medium |
| Webhook Support | Webhook notifications for third-party integrations | Medium |
| i18n/L10n | Multi-language support | High |
| Dark Mode | Theme support in the frontend | Low |

---

## Related Documents

- [Deployment](deployment.md) — production deployment guidance
- [Testing](testing.md) — current test coverage and CI
- [Architecture](architecture.md) — system architecture and limitations
