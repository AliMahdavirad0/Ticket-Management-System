from django.urls import path

from .session_views import (
    csrf_token,
    session_check,
    session_login,
    session_logout,
)
from .views import (
    RegisterView,
    UserProfileView,
    UserUpdateView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
    UserRoleUpdateView,
    available_agents_view,
)

urlpatterns = [
    # ── Session authentication ──
    path('csrf/', csrf_token, name='csrf_token'),
    path('session/', session_check, name='session_check'),
    path('session/login/', session_login, name='session_login'),
    path('session/logout/', session_logout, name='session_logout'),

    # Registration
    path('register/', RegisterView.as_view(), name='register'),

    # User profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UserUpdateView.as_view(), name='user_update'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # User management (admin only)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/role/', UserRoleUpdateView.as_view(), name='user_role_update'),
    path('agents/available/', available_agents_view, name='available_agents'),
]
