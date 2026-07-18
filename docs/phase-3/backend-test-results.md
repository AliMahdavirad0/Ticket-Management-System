# Backend Test Results — Phase 3

**Command:** `python manage.py test accounts.tests tickets.tests dashboard.tests -v 2`
**Working directory:** `backend/`
**Date:** 2026-07-18
**Result:** Ran **77** tests in ~98s — **OK** (0 failures)
**Raw log:** `evidence/backend-test-run.txt`

Requirement IDs refer to `requirements-traceability.md` (mapped from `docs/SRS.pdf`).

| # | Test name | Related requirement | Test scenario | Expected result | Actual result | Pass/Fail |
|--:|-----------|---------------------|---------------|-----------------|---------------|-----------|
| 1 | `accounts.tests.AccountsAPITestCase.test_available_agents_as_admin` | FR-02/FR-12 | Admin lists available agents ordered for assignment UI | HTTP 200 with agent list | 200 OK, 1 agent | **Pass** |
| 2 | `accounts.tests.AccountsAPITestCase.test_available_agents_as_customer_forbidden` | FR-11 | Customer cannot list available agents | HTTP 403 | 403 Forbidden | **Pass** |
| 3 | `accounts.tests.AccountsAPITestCase.test_change_password_success` | FR-10 | Authenticated user changes password with correct old password | HTTP 200; password updated | 200 OK; password changed | **Pass** |
| 4 | `accounts.tests.AccountsAPITestCase.test_change_password_wrong_old_password` | FR-10 | Change password with wrong old password | HTTP 400 | 400 Bad Request | **Pass** |
| 5 | `accounts.tests.AccountsAPITestCase.test_list_users_as_admin` | FR-12 | Admin lists users | HTTP 200; >=3 users | 200 OK; results >= 3 | **Pass** |
| 6 | `accounts.tests.AccountsAPITestCase.test_list_users_as_customer_forbidden` | FR-11 | Customer cannot list users | HTTP 403 | 403 Forbidden | **Pass** |
| 7 | `accounts.tests.AccountsAPITestCase.test_login_invalid_credentials` | FR-10 | Login with wrong password | HTTP 401 | 401 Unauthorized | **Pass** |
| 8 | `accounts.tests.AccountsAPITestCase.test_login_success` | FR-10 | Login with valid credentials returns user payload | HTTP 200; user.username/role | 200 OK; customer1/customer | **Pass** |
| 9 | `accounts.tests.AccountsAPITestCase.test_profile_authenticated` | FR-10/FR-06 | Authenticated profile fetch | HTTP 200; username | 200 OK; customer1 | **Pass** |
| 10 | `accounts.tests.AccountsAPITestCase.test_profile_unauthenticated` | FR-10 | Unauthenticated profile fetch | HTTP 401 | 401 Unauthorized | **Pass** |
| 11 | `accounts.tests.AccountsAPITestCase.test_register_password_mismatch` | FR-10 | Register with mismatched passwords | HTTP 400 | 400 Bad Request | **Pass** |
| 12 | `accounts.tests.AccountsAPITestCase.test_register_success` | FR-10 | Register new customer | HTTP 201; role=customer | 201 Created; role customer | **Pass** |
| 13 | `accounts.tests.AccountsAPITestCase.test_update_profile` | FR-10 | Patch own profile names | HTTP 200; names saved | 200 OK; first_name Test | **Pass** |
| 14 | `accounts.tests.AccountsAPITestCase.test_update_user_role_as_admin` | FR-12 | Admin changes user role to agent | HTTP 200; role=agent | 200 OK; role agent | **Pass** |
| 15 | `accounts.tests.AccountsAPITestCase.test_update_user_role_as_customer_forbidden` | FR-11 | Customer cannot change roles | HTTP 403 | 403 Forbidden | **Pass** |
| 16 | `accounts.tests.AccountsAPITestCase.test_user_detail_as_admin` | FR-12 | Admin retrieves user detail | HTTP 200; username | 200 OK; customer1 | **Pass** |
| 17 | `accounts.tests.UserServiceTestCase.test_create_user` | FR-10/FR-12 | UserService.create_user | User created with role | username/role match | **Pass** |
| 18 | `accounts.tests.UserServiceTestCase.test_create_user_duplicate_username` | FR-10 | Duplicate username rejected | ValueError | ValueError raised | **Pass** |
| 19 | `accounts.tests.UserServiceTestCase.test_get_available_agents_ordered_by_workload` | FR-02/FR-09 | Agents ordered by open/in-progress workload | Lightest agent first | agent_light first | **Pass** |
| 20 | `accounts.tests.UserServiceTestCase.test_get_user_profile_agent` | FR-09/FR-05 | Agent profile includes assigned_tickets stats | assigned_tickets=1 | assigned_tickets=1 | **Pass** |
| 21 | `accounts.tests.UserServiceTestCase.test_get_user_profile_customer` | FR-06 | Customer profile ticket statistics | total/open tickets | total=1 open=1 | **Pass** |
| 22 | `accounts.tests.UserServiceTestCase.test_update_user_role_as_admin` | FR-12 | Service role update by admin | role becomes agent | role agent | **Pass** |
| 23 | `accounts.tests.UserServiceTestCase.test_update_user_role_non_admin_fails` | FR-11 | Non-admin role update denied | PermissionError | PermissionError | **Pass** |
| 24 | `tickets.tests.MessageServiceTestCase.test_admin_can_message_on_closed_ticket` | FR-04/FR-03 | Even admin cannot message CLOSED ticket (current rule) | PermissionError | PermissionError raised | **Pass** |
| 25 | `tickets.tests.MessageServiceTestCase.test_cannot_message_on_closed_ticket` | FR-04/FR-03 | Customer cannot message CLOSED ticket | PermissionError | PermissionError | **Pass** |
| 26 | `tickets.tests.MessageServiceTestCase.test_create_message_as_customer` | FR-04 | Customer creates message on own ticket | Message saved with sender | sender=customer | **Pass** |
| 27 | `tickets.tests.MessageServiceTestCase.test_create_message_wrong_ticket_fails` | FR-04/FR-11 | Other customer cannot message ticket | PermissionError | PermissionError | **Pass** |
| 28 | `tickets.tests.MessageServiceTestCase.test_get_messages_filtered_by_ticket` | FR-04 | Filter messages by ticket_id | count=1 | count=1 | **Pass** |
| 29 | `tickets.tests.MessageServiceTestCase.test_get_messages_for_admin` | FR-04/FR-11 | Admin sees messages | count=1 | count=1 | **Pass** |
| 30 | `tickets.tests.TicketAPITestCase.test_assign_ticket_as_admin` | FR-02 (manual) | Admin assigns agent via API | HTTP 200; assigned_agent set | 200; agent assigned | **Pass** |
| 31 | `tickets.tests.TicketAPITestCase.test_assign_ticket_as_customer_forbidden` | FR-11 | Customer cannot assign | HTTP 403 | 403 | **Pass** |
| 32 | `tickets.tests.TicketAPITestCase.test_change_priority_as_agent` | FR-07 | Agent changes priority | HTTP 200; CRITICAL | 200; CRITICAL | **Pass** |
| 33 | `tickets.tests.TicketAPITestCase.test_change_status_as_agent` | FR-03 | Agent changes status to IN_PROGRESS | HTTP 200; status updated | 200; IN_PROGRESS | **Pass** |
| 34 | `tickets.tests.TicketAPITestCase.test_create_ticket_authenticated` | FR-01 | Authenticated customer creates ticket | HTTP 201; owner=customer | 201; owner customer | **Pass** |
| 35 | `tickets.tests.TicketAPITestCase.test_create_ticket_unauthenticated` | FR-01/FR-10 | Anonymous create denied | HTTP 401 | 401 | **Pass** |
| 36 | `tickets.tests.TicketAPITestCase.test_create_ticket_validation_short_title` | FR-01 | Title too short rejected | HTTP 400 | 400 | **Pass** |
| 37 | `tickets.tests.TicketAPITestCase.test_delete_ticket_as_admin` | FR-12/FR-01 | Admin deletes ticket | HTTP 204; gone | 204; deleted | **Pass** |
| 38 | `tickets.tests.TicketAPITestCase.test_filter_tickets_by_status` | FR-13 | Filter list by status=OPEN | 1 OPEN result | 1 OPEN | **Pass** |
| 39 | `tickets.tests.TicketAPITestCase.test_get_statistics` | FR-05/FR-06 | Ticket statistics endpoint | total/open/resolved counts | total=2 open=1 resolved=1 | **Pass** |
| 40 | `tickets.tests.TicketAPITestCase.test_list_tickets_as_customer` | FR-06/FR-11 | Customer list scoped to own tickets | 1 result | 1 result | **Pass** |
| 41 | `tickets.tests.TicketAPITestCase.test_retrieve_ticket_as_owner` | FR-06 | Owner retrieves ticket detail | HTTP 200; title | 200; title match | **Pass** |
| 42 | `tickets.tests.TicketCategoryAPITestCase.test_create_category_as_admin` | FR-07 | Admin creates category | HTTP 201 | 201 | **Pass** |
| 43 | `tickets.tests.TicketCategoryAPITestCase.test_create_category_as_customer_forbidden` | FR-11 | Customer cannot create category | HTTP 403 | 403 | **Pass** |
| 44 | `tickets.tests.TicketCategoryAPITestCase.test_list_categories_authenticated` | FR-07 | Authenticated list categories | HTTP 200; >=1 | 200; >=1 | **Pass** |
| 45 | `tickets.tests.TicketMessageAPITestCase.test_create_message_as_customer` | FR-04 | API create message | HTTP 201; count=1 | 201; count=1 | **Pass** |
| 46 | `tickets.tests.TicketMessageAPITestCase.test_create_message_on_other_ticket_forbidden` | FR-04/FR-11 | Other user cannot post | HTTP 403 | 403 | **Pass** |
| 47 | `tickets.tests.TicketMessageAPITestCase.test_list_messages_as_customer` | FR-04 | List messages as customer | HTTP 200; 1 result | 200; 1 | **Pass** |
| 48 | `tickets.tests.TicketServiceTestCase.test_admin_can_reopen_closed_ticket` | FR-03 | Admin CLOSED→OPEN | status OPEN | OPEN | **Pass** |
| 49 | `tickets.tests.TicketServiceTestCase.test_agent_cannot_reopen_closed_ticket` | FR-03/FR-11 | Agent cannot reopen CLOSED | ValueError | ValueError | **Pass** |
| 50 | `tickets.tests.TicketServiceTestCase.test_assign_agent_as_admin` | FR-02 (manual) | Service assign by admin | assigned_agent set | agent set | **Pass** |
| 51 | `tickets.tests.TicketServiceTestCase.test_assign_agent_as_customer_fails` | FR-11 | Customer assign denied | PermissionError | PermissionError | **Pass** |
| 52 | `tickets.tests.TicketServiceTestCase.test_change_ticket_priority_as_agent` | FR-07 | Agent priority change | CRITICAL | CRITICAL | **Pass** |
| 53 | `tickets.tests.TicketServiceTestCase.test_change_ticket_priority_as_customer_fails` | FR-11 | Customer priority change denied | PermissionError | PermissionError | **Pass** |
| 54 | `tickets.tests.TicketServiceTestCase.test_change_ticket_status_as_agent` | FR-03 | Agent status change | IN_PROGRESS | IN_PROGRESS | **Pass** |
| 55 | `tickets.tests.TicketServiceTestCase.test_change_ticket_status_as_customer_fails` | FR-03/FR-11 | Customer status change denied | PermissionError | PermissionError | **Pass** |
| 56 | `tickets.tests.TicketServiceTestCase.test_create_ticket` | FR-01 | Service create ticket | OPEN owned by customer | OPEN; owner match | **Pass** |
| 57 | `tickets.tests.TicketServiceTestCase.test_get_tickets_for_admin_sees_all` | FR-05/FR-11 | Admin sees all tickets | count=2 | count=2 | **Pass** |
| 58 | `tickets.tests.TicketServiceTestCase.test_get_tickets_for_agent` | FR-03/FR-11 | Agent sees assigned + unassigned | count=2 | count=2 | **Pass** |
| 59 | `tickets.tests.TicketServiceTestCase.test_get_tickets_for_customer` | FR-06 | Customer sees only own | count=1 | count=1 | **Pass** |
| 60 | `tickets.tests.TicketServiceTestCase.test_invalid_status_transition_open_to_resolved_fails` | FR-03 | OPEN→RESOLVED invalid | ValueError | ValueError | **Pass** |
| 61 | `tickets.tests.TicketServiceTestCase.test_invalid_status_transition_resolved_to_open_fails` | FR-03 | RESOLVED→OPEN invalid | ValueError | ValueError | **Pass** |
| 62 | `tickets.tests.TicketServiceTestCase.test_valid_status_transition_in_progress_to_resolved` | FR-03 | IN_PROGRESS→RESOLVED | RESOLVED | RESOLVED | **Pass** |
| 63 | `tickets.tests.TicketServiceTestCase.test_valid_status_transition_open_to_in_progress` | FR-03 | OPEN→IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | **Pass** |
| 64 | `dashboard.tests.DashboardAPITestCase.test_agents_workload_as_admin` | FR-05/FR-09 | Admin workload endpoint | HTTP 200; agent counts | 200; agent1 total=1 | **Pass** |
| 65 | `dashboard.tests.DashboardAPITestCase.test_agents_workload_as_agent_forbidden` | FR-11 | Agent forbidden on workload | HTTP 403 | 403 | **Pass** |
| 66 | `dashboard.tests.DashboardAPITestCase.test_agents_workload_as_customer_forbidden` | FR-11 | Customer forbidden on workload | HTTP 403 | 403 | **Pass** |
| 67 | `dashboard.tests.DashboardAPITestCase.test_agents_workload_unauthenticated` | FR-10 | Anonymous workload | HTTP 401 | 401 | **Pass** |
| 68 | `dashboard.tests.DashboardAPITestCase.test_overview_as_admin` | FR-05 | Admin dashboard overview | HTTP 200; admin block | 200; admin present | **Pass** |
| 69 | `dashboard.tests.DashboardAPITestCase.test_overview_as_agent` | FR-05 | Agent dashboard overview | HTTP 200; agent metrics | 200; assigned_to_me=1 | **Pass** |
| 70 | `dashboard.tests.DashboardAPITestCase.test_overview_as_customer` | FR-05/FR-06 | Customer dashboard overview | HTTP 200; customer block | 200; customer present | **Pass** |
| 71 | `dashboard.tests.DashboardAPITestCase.test_overview_unauthenticated` | FR-10 | Anonymous dashboard | HTTP 401 | 401 | **Pass** |
| 72 | `dashboard.tests.DashboardServiceTestCase.test_admin_overview_includes_global_metrics` | FR-05 | Admin global ticket/user metrics | admin metrics present | unassigned/users match | **Pass** |
| 73 | `dashboard.tests.DashboardServiceTestCase.test_agent_overview_includes_agent_metrics` | FR-05 | Agent assigned/pool metrics | assigned/pool/attention | values match fixtures | **Pass** |
| 74 | `dashboard.tests.DashboardServiceTestCase.test_customer_overview_includes_customer_metrics` | FR-06 | Customer open/resolved metrics | customer metrics | open=1 resolved_or_closed=1 | **Pass** |
| 75 | `dashboard.tests.DashboardServiceTestCase.test_get_agent_workload_counts` | FR-09 | Workload aggregation | open/in_progress totals | match fixtures | **Pass** |
| 76 | `dashboard.tests.DashboardServiceTestCase.test_recent_messages_in_overview` | FR-04/FR-05 | Recent messages in overview | 1 recent message | 1 message | **Pass** |
| 77 | `dashboard.tests.DashboardServiceTestCase.test_recent_tickets_limited_to_five` | FR-05 | Recent tickets capped at 5 | len=5 | len=5 | **Pass** |

## Statistics

| Metric | Value |
|--------|------:|
| Total tests | 77 |
| Passed | 77 |
| Failed | 0 |
| Errors | 0 |
| Pass rate | 100% |

### By module

| Module | Tests |
|--------|------:|
| `accounts.tests` | 23 |
| `tickets.tests` | 40 |
| `dashboard.tests` | 14 |
| **Total** | **77** |

## Notes

- All Pass/Fail values come from the local Django test runner output (`... ok` / final `OK`).
- No test was marked passed without a matching runner result.
- Warnings in the log (Forbidden/Unauthorized/Bad Request) are expected for negative cases and do not indicate failures.