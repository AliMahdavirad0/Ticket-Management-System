from django.contrib.auth import get_user_model
from django.db.models import Count, Q

User = get_user_model()


class UserService:
    """
    Service layer for user-related business logic.
    """

    @staticmethod
    def create_user(username, email, password, role='customer'):
        """
        Create a new user with validation.
        """
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exists")
        
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        return user

    @staticmethod
    def get_user_profile(user):
        """
        Get user profile with statistics.
        """
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'date_joined': user.date_joined,
        }

        if user.role == 'customer':
            profile_data['statistics'] = {
                'total_tickets': user.tickets.count(),
                'open_tickets': user.tickets.filter(status='OPEN').count(),
                'resolved_tickets': user.tickets.filter(status='RESOLVED').count(),
            }
        elif user.role == 'agent':
            profile_data['statistics'] = {
                'assigned_tickets': user.assigned_tickets.count(),
                'open_assigned': user.assigned_tickets.filter(status='OPEN').count(),
                'resolved_assigned': user.assigned_tickets.filter(status='RESOLVED').count(),
            }

        return profile_data

    @staticmethod
    def get_available_agents():
        """
        Get list of available agents for ticket assignment.
        """
        agents = User.objects.filter(role='agent').annotate(
            assigned_count=Count('assigned_tickets', filter=Q(assigned_tickets__status__in=['OPEN', 'IN_PROGRESS']))
        ).order_by('assigned_count')
        
        return agents

    @staticmethod
    def update_user_role(user_id, new_role, requesting_user):
        """
        Update user role (admin only).
        """
        if requesting_user.role != 'admin':
            raise PermissionError("Only admins can change user roles")

        valid_roles = ['customer', 'agent', 'admin']
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role: {new_role}")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("User does not exist")

        user.role = new_role
        user.save(update_fields=['role'])
        
        return user
