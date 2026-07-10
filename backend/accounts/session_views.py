"""
Session-based authentication views.

Replaces legacy JWT token auth with Django SessionAuthentication.

Flow:
  1. Frontend GETs /api/accounts/csrf/ to obtain a CSRF cookie (unauthenticated).
  2. Frontend POSTs /api/accounts/session/login/ with username + password + X-CSRFToken header.
  3. Backend validates, calls django.contrib.auth.login(), sets sessionid cookie.
  4. On subsequent requests, the browser sends the sessionid cookie automatically.
  5. Frontend includes X-CSRFToken header for all state-changing (POST/PUT/PATCH/DELETE) requests.
"""

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserMinimalSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token(request):
    """
    Set the csrftoken cookie for the frontend.

    The frontend MUST call this endpoint once on app initialization,
    BEFORE attempting any POST/PUT/PATCH/DELETE requests.

    The csrftoken cookie is NOT HttpOnly — JavaScript reads it and
    includes the value as the X-CSRFToken header on unsafe methods.
    """
    return Response({"detail": "CSRF cookie set."})


@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def session_check(request):
    """
    Check if the user has a valid session.

    - Authenticated:  return user data (status 200)
    - Not authenticated: return 401 (no error shown to user)

    Also ensures the CSRF cookie is set on every response
    so the frontend always has a fresh token.
    """
    if request.user.is_authenticated:
        return Response(
            {
                "authenticated": True,
                "user": UserMinimalSerializer(request.user).data,
            }
        )
    return Response({"authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([AllowAny])
def session_login(request):
    """
    Authenticate with username/password and create a Django session.

    Accepts:
      { "username": "...", "password": "..." }

    On success:
      - Sets sessionid cookie (HttpOnly, SameSite=Lax)
      - Sets csrftoken cookie (readable by JS)
      - Returns user data

    On failure:
      - Returns 401 with error detail
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"detail": "Account is disabled."},
            status=status.HTTP_403_FORBIDDEN,
        )

    login(request, user)
    # Ensure CSRF cookie is set in the response
    get_token(request)

    return Response(
        {
            "detail": "Login successful.",
            "user": UserMinimalSerializer(user).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def session_logout(request):
    """
    End the current session.

    Clears the sessionid and csrftoken cookies.
    The frontend should redirect to the login page after calling this.
    """
    logout(request)
    return Response({"detail": "Logged out successfully."})
