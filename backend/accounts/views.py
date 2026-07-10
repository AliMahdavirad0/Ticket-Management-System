from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models as django_models
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .permissions import IsAdmin
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserMinimalSerializer,
    AvailableAgentSerializer,
    UserUpdateSerializer,
    UserRoleUpdateSerializer,
    ChangePasswordSerializer,
)
from .services import UserService


class RegisterView(generics.CreateAPIView):
    """Register a new user (defaults to customer role)."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserProfileView(APIView):
    """Current user profile with role-based statistics."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile_data = UserService.get_user_profile(request.user)
        return Response(profile_data)


class UserUpdateView(generics.UpdateAPIView):
    """Update current user profile (email, first_name, last_name)."""

    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put', 'patch', 'options', 'head']

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK,
        )


class UserListView(generics.ListAPIView):
    """List all users (admin only) with search and role filter."""

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']

    def get_queryset(self):
        qs = User.objects.all().order_by('id')
        search = self.request.query_params.get('search', '')
        role = self.request.query_params.get('role', '')
        if search:
            qs = qs.filter(
                django_models.Q(username__icontains=search) |
                django_models.Q(email__icontains=search) |
                django_models.Q(first_name__icontains=search) |
                django_models.Q(last_name__icontains=search)
            )
        if role:
            qs = qs.filter(role=role)
        return qs


class UserDetailView(generics.RetrieveAPIView):
    """User detail (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserRoleUpdateView(APIView):
    """Update user role (admin only)."""

    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        serializer = UserRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserService.update_user_role(
                user_id=pk,
                new_role=serializer.validated_data['role'],
                requesting_user=request.user,
            )
        except PermissionError as exc:
            raise PermissionDenied(detail=str(exc)) from exc
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)}) from exc

        return Response({
            'message': 'User role updated successfully',
            'user': UserMinimalSerializer(user).data,
        })


@api_view(['GET'])
@permission_classes([IsAdmin])
def available_agents_view(request):
    """Agents sorted by workload (admin only)."""
    agents = UserService.get_available_agents()
    serializer = AvailableAgentSerializer(agents, many=True)
    return Response(serializer.data)
