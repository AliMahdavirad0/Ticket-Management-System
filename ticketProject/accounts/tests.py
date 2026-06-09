from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from tickets.models import Ticket
from .services import UserService

User = get_user_model()


class UserServiceTestCase(TestCase):
    """Tests for UserService business logic."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
        )
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123',
            role='customer',
        )

    def test_create_user(self):
        user = UserService.create_user(
            username='newuser',
            email='new@test.com',
            password='testpass123',
            role='customer',
        )
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.role, 'customer')

    def test_create_user_duplicate_username(self):
        with self.assertRaises(ValueError):
            UserService.create_user(
                username='customer1',
                email='other@test.com',
                password='testpass123',
            )

    def test_get_user_profile_customer(self):
        Ticket.objects.create(
            title='Profile Ticket',
            description='Ticket for profile stats',
            user=self.customer,
            status='OPEN',
        )

        profile = UserService.get_user_profile(self.customer)

        self.assertEqual(profile['username'], 'customer1')
        self.assertEqual(profile['statistics']['total_tickets'], 1)
        self.assertEqual(profile['statistics']['open_tickets'], 1)

    def test_get_user_profile_agent(self):
        agent = User.objects.create_user(
            username='agent1',
            email='agent@test.com',
            password='testpass123',
            role='agent',
        )
        Ticket.objects.create(
            title='Assigned Ticket',
            description='Assigned to agent',
            user=self.customer,
            assigned_agent=agent,
            status='OPEN',
        )

        profile = UserService.get_user_profile(agent)

        self.assertEqual(profile['statistics']['assigned_tickets'], 1)

    def test_update_user_role_as_admin(self):
        user = UserService.update_user_role(
            user_id=self.customer.id,
            new_role='agent',
            requesting_user=self.admin,
        )
        self.assertEqual(user.role, 'agent')

    def test_update_user_role_non_admin_fails(self):
        with self.assertRaises(PermissionError):
            UserService.update_user_role(
                user_id=self.customer.id,
                new_role='agent',
                requesting_user=self.customer,
            )

    def test_get_available_agents_ordered_by_workload(self):
        agent_light = User.objects.create_user(
            username='agent_light',
            email='light@test.com',
            password='testpass123',
            role='agent',
        )
        agent_busy = User.objects.create_user(
            username='agent_busy',
            email='busy@test.com',
            password='testpass123',
            role='agent',
        )
        Ticket.objects.create(
            title='Busy Ticket 1',
            description='Open assigned ticket',
            user=self.customer,
            assigned_agent=agent_busy,
            status='OPEN',
        )
        Ticket.objects.create(
            title='Busy Ticket 2',
            description='In progress assigned ticket',
            user=self.customer,
            assigned_agent=agent_busy,
            status='IN_PROGRESS',
        )

        agents = list(UserService.get_available_agents())

        self.assertEqual(len(agents), 2)
        self.assertEqual(agents[0], agent_light)


class AccountsAPITestCase(APITestCase):
    """Tests for accounts API endpoints."""

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

    def test_register_success(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'newcustomer',
            'email': 'newcustomer@test.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newcustomer')
        self.assertEqual(user.role, 'customer')

    def test_register_password_mismatch(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'baduser',
            'email': 'bad@test.com',
            'password': 'testpass123',
            'password2': 'differentpass',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        response = self.client.post('/api/accounts/session/login/', {
            'username': 'customer1',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'customer1')
        self.assertEqual(response.data['user']['role'], 'customer')

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/accounts/session/login/', {
            'username': 'customer1',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer1')

    def test_profile_unauthenticated(self):
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch('/api/accounts/profile/update/', {
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Test')

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/accounts/change-password/', {
            'old_password': 'testpass123',
            'new_password': 'newpass456789',
            'new_password2': 'newpass456789',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.check_password('newpass456789'))

    def test_change_password_wrong_old_password(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/accounts/change-password/', {
            'old_password': 'wrongold',
            'new_password': 'newpass456789',
            'new_password2': 'newpass456789',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)

    def test_list_users_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/accounts/users/{self.customer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer1')

    def test_update_user_role_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/accounts/users/{self.customer.id}/role/',
            {'role': 'agent'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, 'agent')

    def test_update_user_role_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/accounts/users/{self.agent.id}/role/',
            {'role': 'admin'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_available_agents_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/accounts/agents/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'agent1')

    def test_available_agents_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/accounts/agents/available/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
