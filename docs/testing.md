# Testing

## Backend Tests

### Test Directory Structure

All backend tests are co-located with their respective Django apps using Django's default `tests.py` module:

```
backend/
├── accounts/
│   └── tests.py          # UserService and Accounts API tests
├── tickets/
│   └── tests.py          # TicketService, Ticket API, MessageService tests
└── dashboard/
    └── tests.py          # DashboardService and Dashboard API tests
```

### Running All Backend Tests

```bash
cd backend
python manage.py test accounts.tests tickets.tests dashboard.tests
```

### Running Tests Per Application

```bash
python manage.py test accounts.tests    # Accounts tests
python manage.py test tickets.tests     # Tickets tests
python manage.py test dashboard.tests   # Dashboard tests
```

### Test Breakdown

#### `accounts/tests.py` (17 tests)

**`UserServiceTestCase`** — Unit tests for `UserService` methods:
- `test_create_user` — creates user successfully
- `test_create_user_duplicate_username` — raises ValueError on duplicate
- `test_get_user_profile_customer` — returns correct stats for customer
- `test_get_user_profile_agent` — returns correct stats for agent
- `test_update_user_role_as_admin` — admin can change roles
- `test_update_user_role_non_admin_fails` — non-admin raises PermissionError
- `test_get_available_agents_ordered_by_workload` — agents sorted by assignment count

**`AccountsAPITestCase`** — Integration tests for account API endpoints:
- Registration (success, password mismatch)
- Login (success, invalid credentials)
- Profile (authenticated, unauthenticated)
- Profile update
- Password change (success, wrong old password)
- User list (admin can view, customer forbidden)
- User detail (admin can view)
- Role update (admin can update, customer forbidden)
- Available agents (admin can view, customer forbidden)

#### `tickets/tests.py` (24+ tests)

**`TicketServiceTestCase`** — Unit tests for `TicketService`:
- Creating tickets
- Status transition rules (valid and invalid)
- Agent assignment (admin can, customer cannot)
- Ticket filtering by role (customer sees own, admin sees all, agent sees assigned + unassigned)
- Priority changes (agent can, customer cannot)
- Admin reopening closed tickets
- Agent cannot reopen closed tickets

**`TicketAPITestCase`** — Integration tests for ticket endpoints:
- Create ticket (authenticated, unauthenticated)
- List tickets (customer filtered)
- Change status (agent)
- Statistics endpoint
- Validation (short title)
- Retrieve ticket (owner)
- Assign ticket (admin, customer forbidden)
- Change priority (agent)
- Filter (by status)
- Delete (admin)

**`TicketCategoryAPITestCase`** — Category endpoint tests:
- List categories (authenticated)
- Create category (admin, customer forbidden)

**`TicketMessageAPITestCase`** — Message endpoint tests:
- Create message (customer)
- List messages (customer)
- Message on other ticket forbidden

**`MessageServiceTestCase`** — Unit tests for `MessageService`:
- Create message (customer on own ticket)
- Create message on wrong ticket (forbidden)
- Get messages (admin sees all)
- Filter messages by ticket
- Cannot message on closed ticket
- Admin **cannot** message on closed ticket (note: the test is named `test_admin_can_message_on_closed_ticket` but actually tests that it raises `PermissionError` — there is a naming inconsistency in the test source)

#### `dashboard/tests.py` (12 tests)

**`DashboardServiceTestCase`** — Unit tests for `DashboardService`:
- Customer overview (includes customer metrics, excludes admin/agent)
- Admin overview (includes global metrics, excludes customer/agent)
- Agent overview (includes agent metrics)
- Recent tickets limited to 5
- Recent messages in overview
- Agent workload counts

**`DashboardAPITestCase`** — Integration tests for dashboard endpoints:
- Overview (unauthenticated, as customer, as admin, as agent)
- Agent workload (admin can view, customer/agent forbidden, unauthenticated)

### Test Data Setup

All test cases use Django's test database (created and destroyed per test run). Common setup pattern:

```python
def setUp(self):
    self.client = APIClient()
    self.customer = User.objects.create_user(
        username='customer1', email='customer@test.com',
        password='testpass123', role='customer',
    )
    self.agent = User.objects.create_user(...)
    self.admin = User.objects.create_user(...)
    self.category = TicketCategory.objects.create(name='Technical')
```

Tests use `force_authenticate()` to simulate authenticated requests rather than performing the full login flow.

### Important Tested Business Rules

| Rule | Test Location |
|------|---------------|
| Customers only see own tickets | `TicketServiceTestCase.test_get_tickets_for_customer` |
| Agents see assigned + unassigned | `TicketServiceTestCase.test_get_tickets_for_agent` |
| Admins see all tickets | `TicketServiceTestCase.test_get_tickets_for_admin_sees_all` |
| Customers cannot change status | `TicketServiceTestCase.test_change_ticket_status_as_customer_fails` |
| Agent cannot reopen CLOSED | `TicketServiceTestCase.test_agent_cannot_reopen_closed_ticket` |
| Admin can reopen CLOSED | `TicketServiceTestCase.test_admin_can_reopen_closed_ticket` |
| Invalid transitions blocked | `TicketServiceTestCase.test_invalid_status_transition_*` |
| No messages on CLOSED tickets | `MessageServiceTestCase.test_cannot_message_on_closed_ticket` |
| Non-admin cannot change roles | `UserServiceTestCase.test_update_user_role_non_admin_fails` |

---

## Frontend Validation

The frontend does not have automated test files. Build-time validation provides correctness checks:

```bash
cd frontend

# TypeScript type checking
npx tsc --noEmit

# Production build (includes TypeScript check)
npm run build
```

The frontend project does not include a test runner such as Vitest, Jest, or React Testing Library. Only TypeScript type checking and build validation are configured.

---

## CI Test Execution

The CI pipeline (`.github/workflows/ci.yml`) runs on every push and pull request to the `master` branch:

### Backend Job

1. Checkout repository
2. Set up Python 3.12
3. Install dependencies (`pip install -r requirements.txt`)
4. Run migration check (`makemigrations --check --dry-run`)
5. Run migrations
6. Run system checks
7. Run all tests (`python manage.py test accounts.tests tickets.tests dashboard.tests`)

### Frontend Job

1. Checkout repository
2. Set up Node.js 20 with npm cache
3. Install dependencies (`npm ci`)
4. TypeScript check (`npx tsc --noEmit`)
5. Production build (`npm run build`)

---

## Notes

- **Test count**: The existing README states 69 backend tests. The actual count varies as tests are added or modified.
- **Coverage**: No test coverage tool (like `coverage.py`) is currently configured. Coverage percentages are not available.
- **Frontend tests**: No automated UI or integration tests exist for the frontend. See [Limitations & Roadmap](limitations-and-roadmap.md) for planned improvements.
- **Test isolation**: Each test method creates its own test data in `setUp()` or within the method. Tests use Django's `APITestCase` for API integration tests and `TestCase` for service-layer unit tests.

---

## Related Documents

- [Setup & Development](setup-and-development.md) — running the project locally
- [Deployment](deployment.md) — CI/CD pipeline
- [Limitations & Roadmap](limitations-and-roadmap.md) — planned test improvements
