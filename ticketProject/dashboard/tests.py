from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from tickets.models import Ticket, TicketCategory, TicketMessage
from .services import DashboardService

User = get_user_model()


class DashboardServiceTestCase(TestCase):
    """Tests for DashboardService aggregation logic."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer',
        )
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@test.com',
            password='testpass123',
            role='agent',
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
        )
        self.category = TicketCategory.objects.create(name='Technical')

    def test_customer_overview_includes_customer_metrics(self):
        Ticket.objects.create(
            title='Open Ticket',
            description='Customer open ticket',
            user=self.customer,
            status='OPEN',
        )
        Ticket.objects.create(
            title='Resolved Ticket',
            description='Customer resolved ticket',
            user=self.customer,
            status='RESOLVED',
        )

        overview = DashboardService.get_overview(self.customer)

        self.assertEqual(overview['user']['role'], 'customer')
        self.assertEqual(overview['tickets']['total'], 2)
        self.assertIn('customer', overview)
        self.assertNotIn('admin', overview)
        self.assertNotIn('agent', overview)
        self.assertEqual(overview['customer']['open_tickets'], 1)
        self.assertEqual(overview['customer']['resolved_or_closed'], 1)

    def test_admin_overview_includes_global_metrics(self):
        Ticket.objects.create(
            title='Unassigned Ticket',
            description='Needs assignment',
            user=self.customer,
            assigned_agent=None,
        )
        Ticket.objects.create(
            title='Assigned Ticket',
            description='Assigned to agent',
            user=self.customer,
            assigned_agent=self.agent,
            status='IN_PROGRESS',
        )

        overview = DashboardService.get_overview(self.admin)

        self.assertIn('admin', overview)
        self.assertNotIn('customer', overview)
        self.assertNotIn('agent', overview)
        self.assertEqual(overview['admin']['tickets']['total'], 2)
        self.assertEqual(overview['admin']['tickets']['unassigned'], 1)
        self.assertEqual(overview['admin']['users']['agents'], 1)
        self.assertEqual(overview['admin']['users']['customers'], 1)

    def test_agent_overview_includes_agent_metrics(self):
        Ticket.objects.create(
            title='My Assigned',
            description='Assigned to agent',
            user=self.customer,
            assigned_agent=self.agent,
            status='OPEN',
            priority='HIGH',
        )
        Ticket.objects.create(
            title='Unassigned Pool',
            description='Available in pool',
            user=self.customer,
            assigned_agent=None,
        )

        overview = DashboardService.get_overview(self.agent)

        self.assertIn('agent', overview)
        self.assertNotIn('admin', overview)
        self.assertNotIn('customer', overview)
        self.assertEqual(overview['agent']['assigned_to_me'], 1)
        self.assertEqual(overview['agent']['unassigned_pool'], 1)
        self.assertEqual(overview['agent']['needs_attention'], 1)

    def test_recent_tickets_limited_to_five(self):
        for i in range(7):
            Ticket.objects.create(
                title=f'Ticket {i}',
                description='Test ticket description',
                user=self.customer,
            )

        overview = DashboardService.get_overview(self.customer)

        self.assertEqual(len(overview['recent_tickets']), 5)

    def test_recent_messages_in_overview(self):
        ticket = Ticket.objects.create(
            title='Message Ticket',
            description='Ticket with messages',
            user=self.customer,
        )
        TicketMessage.objects.create(
            ticket=ticket,
            sender=self.customer,
            message='First message on ticket',
        )

        overview = DashboardService.get_overview(self.customer)

        self.assertEqual(overview['messages']['total'], 1)
        self.assertEqual(len(overview['recent_messages']), 1)
        self.assertEqual(overview['recent_messages'][0]['ticket_id'], ticket.id)

    def test_get_agent_workload_counts(self):
        Ticket.objects.create(
            title='Agent Open',
            description='Open assigned ticket',
            user=self.customer,
            assigned_agent=self.agent,
            status='OPEN',
        )
        Ticket.objects.create(
            title='Agent In Progress',
            description='In progress assigned ticket',
            user=self.customer,
            assigned_agent=self.agent,
            status='IN_PROGRESS',
        )

        workload = DashboardService.get_agent_workload()

        self.assertEqual(len(workload), 1)
        self.assertEqual(workload[0]['username'], 'agent1')
        self.assertEqual(workload[0]['assigned_total'], 2)
        self.assertEqual(workload[0]['open'], 1)
        self.assertEqual(workload[0]['in_progress'], 1)


class DashboardAPITestCase(APITestCase):
    """Tests for dashboard API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer',
        )
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@test.com',
            password='testpass123',
            role='agent',
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
        )

    def test_overview_unauthenticated(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_overview_as_customer(self):
        Ticket.objects.create(
            title='Customer Ticket',
            description='Customer owned ticket',
            user=self.customer,
            status='OPEN',
        )

        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'customer1')
        self.assertEqual(response.data['tickets']['total'], 1)
        self.assertIn('customer', response.data)
        self.assertNotIn('admin', response.data)
        self.assertNotIn('agent', response.data)

    def test_overview_as_admin(self):
        Ticket.objects.create(
            title='System Ticket',
            description='Ticket visible to admin',
            user=self.customer,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('admin', response.data)
        self.assertEqual(response.data['admin']['tickets']['total'], 1)

    def test_overview_as_agent(self):
        Ticket.objects.create(
            title='Assigned Ticket',
            description='Ticket assigned to agent',
            user=self.customer,
            assigned_agent=self.agent,
        )

        self.client.force_authenticate(user=self.agent)
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('agent', response.data)
        self.assertEqual(response.data['agent']['assigned_to_me'], 1)

    def test_agents_workload_as_admin(self):
        Ticket.objects.create(
            title='Workload Ticket',
            description='Assigned for workload',
            user=self.customer,
            assigned_agent=self.agent,
            status='OPEN',
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/dashboard/agents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'agent1')
        self.assertEqual(response.data[0]['assigned_total'], 1)

    def test_agents_workload_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/dashboard/agents/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agents_workload_as_agent_forbidden(self):
        self.client.force_authenticate(user=self.agent)
        response = self.client.get('/api/dashboard/agents/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agents_workload_unauthenticated(self):
        response = self.client.get('/api/dashboard/agents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
