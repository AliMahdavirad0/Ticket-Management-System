"""
Central role-based permissions for all apps.

Unauthenticated requests raise NotAuthenticated (401).
Authenticated users with the wrong role receive PermissionDenied (403).
"""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied


# Role constants (API contract uses "customer" as the end-user role)
ROLE_CUSTOMER = 'customer'
ROLE_AGENT = 'agent'
ROLE_ADMIN = 'admin'

VALID_ROLES = (ROLE_CUSTOMER, ROLE_AGENT, ROLE_ADMIN)


def user_has_role(user, *roles):
    return getattr(user, 'role', None) in roles


def require_authenticated(request):
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated(
            detail='Authentication credentials were not provided.',
            code='not_authenticated',
        )


def require_role(request, *roles, message=None):
    """Raise NotAuthenticated or PermissionDenied with clear messages."""
    require_authenticated(request)
    if not user_has_role(request.user, *roles):
        raise PermissionDenied(
            detail=message or f'This action requires one of these roles: {", ".join(roles)}.',
            code='permission_denied',
        )


class RolePermission(BasePermission):
    """
    Base permission: authenticated user with role in ``allowed_roles``.
    """

    allowed_roles = ()
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        require_authenticated(request)
        if not user_has_role(request.user, *self.allowed_roles):
            self.message = (
                f'This action requires one of these roles: '
                f'{", ".join(self.allowed_roles)}.'
            )
            return False
        return True


class IsAdmin(RolePermission):
    allowed_roles = (ROLE_ADMIN,)
    message = 'Admin access required.'


class IsAgent(RolePermission):
    allowed_roles = (ROLE_AGENT,)
    message = 'Agent access required.'


class IsCustomer(RolePermission):
    allowed_roles = (ROLE_CUSTOMER,)
    message = 'Customer access required.'


class IsAgentOrAdmin(RolePermission):
    allowed_roles = (ROLE_AGENT, ROLE_ADMIN)
    message = 'Agent or admin access required.'


class IsAuthenticatedNonAdmin(RolePermission):
    """Customer or agent (any authenticated non-admin)."""

    allowed_roles = (ROLE_CUSTOMER, ROLE_AGENT)
    message = 'Access denied for this role.'
