from django.db import transaction
from django.db.models import Q, Prefetch, Count
from accounts.models import User
from tickets.models import Ticket, TicketMessage


class TicketService:
    """
    Service layer for ticket-related business logic.
    Separates business logic from views for better maintainability.
    """

    @staticmethod
    def get_tickets_for_user(user):
        """
        Get tickets based on user role with optimized queries.
        """
        queryset = Ticket.objects.select_related(
            'user',
            'assigned_agent',
            'category'
        ).annotate(
            message_count=Count('messages')
        ).prefetch_related(
            Prefetch(
                'messages',
                queryset=TicketMessage.objects.select_related('sender').order_by('-created_at'),
                to_attr='_prefetched_messages_for_detail'
            )
        )

        if user.role == 'admin':
            return queryset
        elif user.role == 'agent':
            return queryset.filter(
                Q(assigned_agent=user) | Q(assigned_agent__isnull=True)
            )
        else:  # customer
            return queryset.filter(user=user)

    @staticmethod
    def create_ticket(user, validated_data):
        """
        Create a new ticket for a user.
        """
        ticket = Ticket.objects.create(
            user=user,
            **validated_data
        )
        return ticket

    @staticmethod
    def change_ticket_status(ticket, new_status, user):
        """
        Change ticket status with validation and transition rules.

        Valid transitions:
            OPEN → IN_PROGRESS, CLOSED
            IN_PROGRESS → RESOLVED, CLOSED
            RESOLVED → IN_PROGRESS, CLOSED
            CLOSED → OPEN (admin only)
        """
        valid_statuses = [choice[0] for choice in Ticket.Status.choices]

        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")

        # Business rule: Only agents/admins can change status
        if user.role not in ['agent', 'admin']:
            raise PermissionError("Only agents and admins can change ticket status")

        # Validate transition rules
        VALID_TRANSITIONS = {
            'OPEN': ['IN_PROGRESS', 'CLOSED'],
            'IN_PROGRESS': ['RESOLVED', 'CLOSED'],
            'RESOLVED': ['IN_PROGRESS', 'CLOSED'],
            'CLOSED': ['OPEN'] if user.role == 'admin' else [],
        }

        allowed = VALID_TRANSITIONS.get(ticket.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot change status from '{ticket.status}' to '{new_status}'. "
                f"Allowed transitions: {', '.join(allowed) if allowed else 'none'}"
            )

        ticket.status = new_status
        ticket.save(update_fields=['status', 'updated_at'])

        return ticket

    @staticmethod
    def assign_agent_to_ticket(ticket, agent_id, user):
        """
        Assign an agent to a ticket.
        """
        # Business rule: Only admins can assign agents
        if user.role != 'admin':
            raise PermissionError("Only admins can assign agents")

        try:
            agent = User.objects.get(id=agent_id, role='agent')
        except User.DoesNotExist:
            raise ValueError("Invalid agent ID or user is not an agent")

        ticket.assigned_agent = agent
        ticket.save(update_fields=['assigned_agent', 'updated_at'])
        
        return ticket

    @staticmethod
    def change_ticket_priority(ticket, new_priority, user):
        """
        Change ticket priority.
        """
        valid_priorities = [choice[0] for choice in Ticket.Priority.choices]
        
        if new_priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {new_priority}")

        # Business rule: Agents and admins can change priority
        if user.role not in ['agent', 'admin']:
            raise PermissionError("Only agents and admins can change priority")

        ticket.priority = new_priority
        ticket.save(update_fields=['priority', 'updated_at'])
        
        return ticket

    @staticmethod
    def get_ticket_statistics(user):
        """
        Get ticket statistics based on user role.
        """
        queryset = TicketService.get_tickets_for_user(user)
        
        stats = {
            'total': queryset.count(),
            'open': queryset.filter(status=Ticket.Status.OPEN).count(),
            'in_progress': queryset.filter(status=Ticket.Status.IN_PROGRESS).count(),
            'resolved': queryset.filter(status=Ticket.Status.RESOLVED).count(),
            'closed': queryset.filter(status=Ticket.Status.CLOSED).count(),
            'by_priority': {
                'low': queryset.filter(priority=Ticket.Priority.LOW).count(),
                'medium': queryset.filter(priority=Ticket.Priority.MEDIUM).count(),
                'high': queryset.filter(priority=Ticket.Priority.HIGH).count(),
                'critical': queryset.filter(priority=Ticket.Priority.CRITICAL).count(),
            }
        }
        
        return stats
