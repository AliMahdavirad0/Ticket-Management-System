from django.db.models import Q
from tickets.models import TicketMessage, Ticket


class MessageService:
    """
    Service layer for ticket message-related business logic.
    """

    @staticmethod
    def get_messages_for_user(user, ticket_id=None):
        """
        Get messages based on user role and optional ticket filter.
        """
        queryset = TicketMessage.objects.select_related(
            'ticket',
            'sender',
            'ticket__user',
            'ticket__assigned_agent'
        )

        if user.role == 'admin':
            # Admins can see all messages
            pass
        elif user.role == 'agent':
            # Agents can see messages from tickets assigned to them
            queryset = queryset.filter(
                Q(ticket__assigned_agent=user) | Q(ticket__assigned_agent__isnull=True)
            )
        else:  # customer
            # Customers can only see messages from their own tickets
            queryset = queryset.filter(ticket__user=user)

        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)

        return queryset.order_by('created_at')

    @staticmethod
    def create_message(user, ticket_id, message_content):
        """
        Create a new message for a ticket with validation.
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValueError("Ticket does not exist")

        # Validate user can access this ticket
        if user.role == 'customer' and ticket.user != user:
            raise PermissionError("You can only add messages to your own tickets")
        elif user.role == 'agent' and ticket.assigned_agent != user and ticket.assigned_agent is not None:
            raise PermissionError("You can only add messages to tickets assigned to you")

        message = TicketMessage.objects.create(
            ticket=ticket,
            sender=user,
            message=message_content
        )

        # Update ticket's updated_at timestamp
        ticket.save(update_fields=['updated_at'])

        return message

    @staticmethod
    def validate_message_access(user, message):
        """
        Validate if user can access a specific message.
        """
        if user.role == 'admin':
            return True
        elif user.role == 'agent':
            return message.ticket.assigned_agent == user or message.ticket.assigned_agent is None
        else:  # customer
            return message.ticket.user == user
