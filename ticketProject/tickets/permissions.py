"""
Ticket and message object-level permissions.

Role-based view permissions live in ``accounts.permissions``.
"""

from rest_framework.permissions import BasePermission

from accounts.permissions import (
    IsAdmin,
    IsAgent,
    IsCustomer,
    IsAgentOrAdmin,
    ROLE_ADMIN,
    ROLE_AGENT,
    ROLE_CUSTOMER,
    require_authenticated,
    user_has_role,
)

__all__ = [
    'IsAdmin',
    'IsAgent',
    'IsCustomer',
    'IsAgentOrAdmin',
    'IsTicketOwnerOrAgentOrAdmin',
    'CanModifyTicket',
    'CanDeleteTicket',
    'IsMessageOwnerOrTicketParticipant',
]


class IsTicketOwnerOrAgentOrAdmin(BasePermission):
    """Object-level: ticket owner, assigned agent, unassigned pool (agents), or admin."""

    message = 'You do not have access to this ticket.'

    def has_permission(self, request, view):
        require_authenticated(request)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user_has_role(user, ROLE_ADMIN):
            return True

        if hasattr(obj, 'user') and obj.user_id == user.id:
            return True

        if user_has_role(user, ROLE_AGENT) and hasattr(obj, 'assigned_agent'):
            return obj.assigned_agent_id == user.id or obj.assigned_agent_id is None

        return False


class CanModifyTicket(BasePermission):
    """Customers: own OPEN tickets. Agents: assigned or unassigned. Admins: all."""

    message = 'You cannot modify this ticket.'

    def has_permission(self, request, view):
        require_authenticated(request)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user_has_role(user, ROLE_ADMIN):
            return True

        if user_has_role(user, ROLE_AGENT):
            return (
                obj.assigned_agent_id == user.id
                or obj.assigned_agent_id is None
            )

        if user_has_role(user, ROLE_CUSTOMER) and obj.user_id == user.id:
            return obj.status == 'OPEN'

        return False


class CanDeleteTicket(BasePermission):
    """Admins: any ticket. Customers: own OPEN tickets only."""

    message = 'You cannot delete this ticket.'

    def has_permission(self, request, view):
        require_authenticated(request)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user_has_role(user, ROLE_ADMIN):
            return True

        if (
            user_has_role(user, ROLE_CUSTOMER)
            and obj.user_id == user.id
            and obj.status == 'OPEN'
        ):
            return True

        return False


class IsMessageOwnerOrTicketParticipant(BasePermission):
    """Message sender, ticket owner, assigned agent, or admin."""

    message = 'You do not have access to this message.'

    def has_permission(self, request, view):
        require_authenticated(request)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user_has_role(user, ROLE_ADMIN):
            return True

        if hasattr(obj, 'sender') and obj.sender_id == user.id:
            return True

        if hasattr(obj, 'ticket') and obj.ticket.user_id == user.id:
            return True

        if user_has_role(user, ROLE_AGENT) and hasattr(obj, 'ticket'):
            ticket = obj.ticket
            return (
                ticket.assigned_agent_id == user.id
                or ticket.assigned_agent_id is None
            )

        return False
