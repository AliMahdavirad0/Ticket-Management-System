"""
Consistent API error responses across all apps.
"""

from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
    AuthenticationFailed,
)


def _normalize_errors(data):
    """Flatten validation errors into a consistent shape."""
    if isinstance(data, list):
        return {'non_field_errors': data}
    if isinstance(data, dict):
        return data
    return {'non_field_errors': [str(data)]}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    status_code = response.status_code
    original = response.data

    if status_code == 400 and isinstance(exc, ValidationError):
        errors = _normalize_errors(original)
        response.data = {
            'detail': 'Validation failed.',
            'errors': errors,
            **errors,
        }
        return response

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        detail = original.get('detail', str(exc)) if isinstance(original, dict) else str(exc)

        # DRF coerces 401 → 403 when the first auth class returns no
        # WWW-Authenticate header (SessionAuthentication). Preserve 401
        # so the frontend axios interceptor correctly redirects to login.
        response.status_code = status.HTTP_401_UNAUTHORIZED

        response.data = {
            'detail': detail,
            'code': getattr(exc, 'default_code', 'not_authenticated'),
        }
        return response

    if isinstance(exc, PermissionDenied):
        detail = original.get('detail', str(exc)) if isinstance(original, dict) else str(exc)
        response.data = {
            'detail': detail,
            'code': getattr(exc, 'default_code', 'permission_denied'),
        }
        return response

    if isinstance(original, dict) and 'detail' not in original:
        if len(original) == 1 and 'detail' in str(original):
            pass
        elif status_code >= 400:
            response.data = {
                'detail': original.get('detail', 'Request failed.'),
                'errors': _normalize_errors(original),
            }

    return response
