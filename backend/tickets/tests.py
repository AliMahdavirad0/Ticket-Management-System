from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Ticket, TicketCategory, TicketMessage
from .services import TicketService, MessageService

User = get_user_model()


class TicketServiceTestCase(TestCase):
    """Test cases for TicketService business logic."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer'
        )
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@test.com',
            password='testpass123',
            role='agent'
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.category = TicketCategory.objects.create(name='Technical')

    def test_create_ticket(self):
        """Test ticket creation through service."""
        ticket_data = {
            'title': 'Test Ticket',
            'description': 'This is a test ticket description',
            'priority': 'HIGH',
            'category': self.category
        }
        ticket = TicketService.create_ticket(self.customer, ticket_data)
        
        self.assertEqual(ticket.user, self.customer)
        self.assertEqual(ticket.title, 'Test Ticket')
        self.assertEqual(ticket.status, 'OPEN')

    def test_change_ticket_status_as_agent(self):
        """Test that agents can change ticket status."""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            user=self.customer,
            assigned_agent=self.agent
        )
        
        updated_ticket = TicketService.change_ticket_status(
            ticket, 'IN_PROGRESS', self.agent
        )
        
        self.assertEqual(updated_ticket.status, 'IN_PROGRESS')

    def test_change_ticket_status_as_customer_fails(self):
        """Test that customers cannot change ticket status."""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            user=self.customer
        )
        
        with self.assertRaises(PermissionError):
            TicketService.change_ticket_status(ticket, 'CLOSED', self.customer)

    def test_assign_agent_as_admin(self):
        """Test that admins can assign agents to tickets."""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            user=self.customer
        )
        
        updated_ticket = TicketService.assign_agent_to_ticket(
            ticket, self.agent.id, self.admin
        )
        
        self.assertEqual(updated_ticket.assigned_agent, self.agent)

    def test_get_tickets_for_customer(self):
        """Test that customers only see their own tickets."""
        Ticket.objects.create(
            title='Customer Ticket',
            description='Test',
            user=self.customer
        )
        other_customer = User.objects.create_user(
            username='customer2',
            email='customer2@test.com',
            password='testpass123',
            role='customer'
        )
        Ticket.objects.create(
            title='Other Ticket',
            description='Test',
            user=other_customer
        )
        
        tickets = TicketService.get_tickets_for_user(self.customer)
        self.assertEqual(tickets.count(), 1)
        self.assertEqual(tickets.first().user, self.customer)

    def test_get_tickets_for_admin_sees_all(self):
        Ticket.objects.create(
            title='Ticket A',
            description='Test description',
            user=self.customer,
        )
        Ticket.objects.create(
            title='Ticket B',
            description='Another test ticket',
            user=self.customer,
        )
        tickets = TicketService.get_tickets_for_user(self.admin)
        self.assertEqual(tickets.count(), 2)

    def test_get_tickets_for_agent(self):
        Ticket.objects.create(
            title='Assigned',
            description='Assigned to agent',
            user=self.customer,
            assigned_agent=self.agent,
        )
        Ticket.objects.create(
            title='Unassigned',
            description='Unassigned pool ticket',
            user=self.customer,
        )
        Ticket.objects.create(
            title='Other Agent',
            description='Assigned to someone else',
            user=self.customer,
            assigned_agent=self.admin,
        )
        tickets = TicketService.get_tickets_for_user(self.agent)
        self.assertEqual(tickets.count(), 2)

    def test_assign_agent_as_customer_fails(self):
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            user=self.customer,
        )
        with self.assertRaises(PermissionError):
            TicketService.assign_agent_to_ticket(
                ticket, self.agent.id, self.customer
            )

    def test_change_ticket_priority_as_agent(self):
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            user=self.customer,
            assigned_agent=self.agent,
        )
        updated = TicketService.change_ticket_priority(
            ticket, 'CRITICAL', self.agent
        )
        self.assertEqual(updated.priority, 'CRITICAL')

    def test_change_ticket_priority_as_customer_fails(self):
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            user=self.customer,
        )
        with self.assertRaises(PermissionError):
            TicketService.change_ticket_priority(ticket, 'HIGH', self.customer)

    def test_valid_status_transition_open_to_in_progress(self):
        ticket = Ticket.objects.create(
            title='Status Transition', description='Test',
            user=self.customer, assigned_agent=self.agent,
        )
        updated = TicketService.change_ticket_status(ticket, 'IN_PROGRESS', self.agent)
        self.assertEqual(updated.status, 'IN_PROGRESS')

    def test_valid_status_transition_in_progress_to_resolved(self):
        ticket = Ticket.objects.create(
            title='Status Transition', description='Test',
            user=self.customer, assigned_agent=self.agent,
            status='IN_PROGRESS',
        )
        updated = TicketService.change_ticket_status(ticket, 'RESOLVED', self.agent)
        self.assertEqual(updated.status, 'RESOLVED')

    def test_invalid_status_transition_open_to_resolved_fails(self):
        ticket = Ticket.objects.create(
            title='Invalid Transition', description='Test',
            user=self.customer, assigned_agent=self.agent,
            status='OPEN',
        )
        with self.assertRaises(ValueError):
            TicketService.change_ticket_status(ticket, 'RESOLVED', self.agent)

    def test_invalid_status_transition_resolved_to_open_fails(self):
        ticket = Ticket.objects.create(
            title='Invalid Transition', description='Test',
            user=self.customer, assigned_agent=self.agent,
            status='RESOLVED',
        )
        with self.assertRaises(ValueError):
            TicketService.change_ticket_status(ticket, 'OPEN', self.agent)

    def test_admin_can_reopen_closed_ticket(self):
        ticket = Ticket.objects.create(
            title='Reopen', description='Test',
            user=self.customer, assigned_agent=self.agent,
            status='CLOSED',
        )
        updated = TicketService.change_ticket_status(ticket, 'OPEN', self.admin)
        self.assertEqual(updated.status, 'OPEN')

    def test_agent_cannot_reopen_closed_ticket(self):
        ticket = Ticket.objects.create(
            title='Reopen Attempt', description='Test',
            user=self.customer, assigned_agent=self.agent,
            status='CLOSED',
        )
        with self.assertRaises(ValueError):
            TicketService.change_ticket_status(ticket, 'OPEN', self.agent)


class TicketAPITestCase(APITestCase):
    """Test cases for Ticket API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer'
        )
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@test.com',
            password='testpass123',
            role='agent'
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.category = TicketCategory.objects.create(name='Technical')

    def test_create_ticket_authenticated(self):
        """Test creating a ticket as authenticated customer."""
        self.client.force_authenticate(user=self.customer)
        
        data = {
            'title': 'API Test Ticket',
            'description': 'This is a test ticket from API',
            'priority': 'MEDIUM',
            'category': self.category.id
        }
        
        response = self.client.post('/api/tickets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Ticket.objects.first().user, self.customer)

    def test_create_ticket_unauthenticated(self):
        """Test that unauthenticated users cannot create tickets."""
        data = {
            'title': 'API Test Ticket',
            'description': 'This is a test ticket from API',
            'priority': 'MEDIUM'
        }
        
        response = self.client.post('/api/tickets/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tickets_as_customer(self):
        """Test that customers only see their own tickets."""
        self.client.force_authenticate(user=self.customer)
        
        Ticket.objects.create(
            title='My Ticket',
            description='Test',
            user=self.customer
        )
        
        other_customer = User.objects.create_user(
            username='customer2',
            email='customer2@test.com',
            password='testpass123',
            role='customer'
        )
        Ticket.objects.create(
            title='Other Ticket',
            description='Test',
            user=other_customer
        )
        
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_change_status_as_agent(self):
        """Test that agents can change ticket status."""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test',
            user=self.customer,
            assigned_agent=self.agent
        )
        
        self.client.force_authenticate(user=self.agent)
        response = self.client.patch(
            f'/api/tickets/{ticket.id}/change_status/',
            {'status': 'IN_PROGRESS'},
            format='json',
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'IN_PROGRESS')

    def test_get_statistics(self):
        """Test ticket statistics endpoint."""
        self.client.force_authenticate(user=self.customer)
        
        Ticket.objects.create(
            title='Open Ticket',
            description='Test',
            user=self.customer,
            status='OPEN'
        )
        Ticket.objects.create(
            title='Resolved Ticket',
            description='Test',
            user=self.customer,
            status='RESOLVED'
        )
        
        response = self.client.get('/api/tickets/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['open'], 1)
        self.assertEqual(response.data['resolved'], 1)

    def test_create_ticket_validation_short_title(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/tickets/', {
            'title': 'Bad',
            'description': 'This description is long enough',
            'priority': 'LOW',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ticket_as_owner(self):
        ticket = Ticket.objects.create(
            title='Retrieve Ticket',
            description='Ticket detail test',
            user=self.customer,
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/tickets/{ticket.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Retrieve Ticket')

    def test_assign_ticket_as_admin(self):
        ticket = Ticket.objects.create(
            title='Assign Ticket',
            description='Needs an agent',
            user=self.customer,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/tickets/{ticket.id}/assign/',
            {'agent_id': self.agent.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.assigned_agent, self.agent)

    def test_assign_ticket_as_customer_forbidden(self):
        ticket = Ticket.objects.create(
            title='Assign Ticket',
            description='Customer cannot assign',
            user=self.customer,
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/tickets/{ticket.id}/assign/',
            {'agent_id': self.agent.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_priority_as_agent(self):
        ticket = Ticket.objects.create(
            title='Priority Ticket',
            description='Change priority test',
            user=self.customer,
            assigned_agent=self.agent,
        )
        self.client.force_authenticate(user=self.agent)
        response = self.client.patch(
            f'/api/tickets/{ticket.id}/change_priority/',
            {'priority': 'CRITICAL'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.priority, 'CRITICAL')

    def test_filter_tickets_by_status(self):
        Ticket.objects.create(
            title='Open Ticket',
            description='Open status ticket',
            user=self.customer,
            status='OPEN',
        )
        Ticket.objects.create(
            title='Closed Ticket',
            description='Closed status ticket',
            user=self.customer,
            status='CLOSED',
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/tickets/?status=OPEN')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'OPEN')

    def test_delete_ticket_as_admin(self):
        ticket = Ticket.objects.create(
            title='Delete Ticket',
            description='Admin can delete',
            user=self.customer,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/tickets/{ticket.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())


class TicketCategoryAPITestCase(APITestCase):
    """Tests for ticket category endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer',
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
        )
        self.category = TicketCategory.objects.create(name='Technical')

    def test_list_categories_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_create_category_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/categories/', {'name': 'Billing'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/categories/', {'name': 'Forbidden'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TicketMessageAPITestCase(APITestCase):
    """Tests for ticket message endpoints."""

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
        self.ticket = Ticket.objects.create(
            title='Message Ticket',
            description='Ticket for messages',
            user=self.customer,
            assigned_agent=self.agent,
        )

    def test_create_message_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/messages/', {
            'ticket': self.ticket.id,
            'message': 'Customer follow-up message',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TicketMessage.objects.count(), 1)

    def test_list_messages_as_customer(self):
        TicketMessage.objects.create(
            ticket=self.ticket,
            sender=self.customer,
            message='Existing message',
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_message_on_other_ticket_forbidden(self):
        other = User.objects.create_user(
            username='customer2',
            email='customer2@test.com',
            password='testpass123',
            role='customer',
        )
        self.client.force_authenticate(user=other)
        response = self.client.post('/api/messages/', {
            'ticket': self.ticket.id,
            'message': 'Should not be allowed',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MessageServiceTestCase(TestCase):
    """Test cases for MessageService business logic."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer'
        )
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@test.com',
            password='testpass123',
            role='agent'
        )
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test',
            user=self.customer,
            assigned_agent=self.agent
        )

    def test_create_message_as_customer(self):
        """Test that customers can add messages to their tickets."""
        message = MessageService.create_message(
            user=self.customer,
            ticket_id=self.ticket.id,
            message_content='This is a test message'
        )
        
        self.assertEqual(message.sender, self.customer)
        self.assertEqual(message.ticket, self.ticket)

    def test_create_message_wrong_ticket_fails(self):
        """Test that customers cannot add messages to other tickets."""
        other_customer = User.objects.create_user(
            username='customer2',
            email='customer2@test.com',
            password='testpass123',
            role='customer'
        )
        
        with self.assertRaises(PermissionError):
            MessageService.create_message(
                user=other_customer,
                ticket_id=self.ticket.id,
                message_content='Unauthorized message'
            )

    def test_get_messages_for_admin(self):
        TicketMessage.objects.create(
            ticket=self.ticket,
            sender=self.customer,
            message='Admin visible message',
        )
        admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
        )
        messages = MessageService.get_messages_for_user(admin)
        self.assertEqual(messages.count(), 1)

    def test_get_messages_filtered_by_ticket(self):
        other_ticket = Ticket.objects.create(
            title='Other Ticket',
            description='Second ticket',
            user=self.customer,
        )
        TicketMessage.objects.create(
            ticket=self.ticket,
            sender=self.customer,
            message='On first ticket',
        )
        TicketMessage.objects.create(
            ticket=other_ticket,
            sender=self.customer,
            message='On second ticket',
        )
        messages = MessageService.get_messages_for_user(
            self.customer,
            ticket_id=self.ticket.id,
        )
        self.assertEqual(messages.count(), 1)

    def test_cannot_message_on_closed_ticket(self):
        self.ticket.status = 'CLOSED'
        self.ticket.save(update_fields=['status'])
        with self.assertRaises(PermissionError):
            MessageService.create_message(
                user=self.customer,
                ticket_id=self.ticket.id,
                message_content='This should be blocked',
            )

    def test_admin_can_message_on_closed_ticket(self):
        self.ticket.status = 'CLOSED'
        self.ticket.save(update_fields=['status'])
        admin = User.objects.create_user(
            username='admin1', email='admin@test.com',
            password='testpass123', role='admin',
        )
        with self.assertRaises(PermissionError):
            MessageService.create_message(
                user=admin,
                ticket_id=self.ticket.id,
                message_content='Admin message on closed ticket',
            )
