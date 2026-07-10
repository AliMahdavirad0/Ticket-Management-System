from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Ticket, TicketCategory, TicketMessage
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    TicketCategorySerializer,
    TicketMessageSerializer,
    TicketMessageCreateSerializer,
    TicketStatusChangeSerializer,
    TicketAssignSerializer,
    TicketPriorityChangeSerializer,
)
from accounts.permissions import IsAdmin, IsAgentOrAdmin
from .permissions import (
    IsTicketOwnerOrAgentOrAdmin,
    CanModifyTicket,
    CanDeleteTicket,
    IsMessageOwnerOrTicketParticipant,
)
from .services import TicketService, MessageService


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tickets.
    
    Provides CRUD operations and custom actions for ticket management.
    Uses service layer for business logic.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_agent']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get tickets based on user role using service layer."""
        return TicketService.get_tickets_for_user(self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TicketListSerializer
        if self.action == 'retrieve':
            return TicketDetailSerializer
        if self.action == 'create':
            return TicketCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        if self.action == 'change_status':
            return TicketStatusChangeSerializer
        if self.action == 'assign':
            return TicketAssignSerializer
        if self.action == 'change_priority':
            return TicketPriorityChangeSerializer
        if self.action == 'statistics':
            return TicketListSerializer
        return TicketDetailSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'change_status':
            return [IsAgentOrAdmin()]
        if self.action == 'assign':
            return [IsAdmin()]
        if self.action == 'change_priority':
            return [IsAgentOrAdmin()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), CanModifyTicket()]
        if self.action == 'destroy':
            return [IsAuthenticated(), CanDeleteTicket()]
        if self.action in ['retrieve', 'list']:
            return [IsAuthenticated(), IsTicketOwnerOrAgentOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Create ticket using service layer."""
        ticket = TicketService.create_ticket(
            user=self.request.user,
            validated_data=serializer.validated_data
        )
        serializer.instance = ticket

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[IsAgentOrAdmin],
        serializer_class=TicketStatusChangeSerializer
    )
    def change_status(self, request, pk=None):
        """
        Change ticket status.
        
        Only agents and admins can change status.
        """
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_ticket = TicketService.change_ticket_status(
                ticket=ticket,
                new_status=serializer.validated_data['status'],
                user=request.user
            )
        except PermissionError as exc:
            raise PermissionDenied(detail=str(exc)) from exc
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)}) from exc

        serializer = TicketDetailSerializer(updated_ticket, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[IsAdmin],
        serializer_class=TicketAssignSerializer
    )
    def assign(self, request, pk=None):
        """
        Assign agent to ticket.
        
        Only admins can assign agents.
        """
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_ticket = TicketService.assign_agent_to_ticket(
                ticket=ticket,
                agent_id=serializer.validated_data['agent_id'],
                user=request.user
            )
        except PermissionError as exc:
            raise PermissionDenied(detail=str(exc)) from exc
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)}) from exc

        serializer = TicketDetailSerializer(updated_ticket, context={'request': request})
        return Response({
            'message': 'Agent assigned successfully',
            'agent': updated_ticket.assigned_agent.username,
            'ticket': serializer.data,
        })

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[IsAgentOrAdmin],
        serializer_class=TicketPriorityChangeSerializer
    )
    def change_priority(self, request, pk=None):
        """
        Change ticket priority.
        
        Agents and admins can change priority.
        """
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_ticket = TicketService.change_ticket_priority(
                ticket=ticket,
                new_priority=serializer.validated_data['priority'],
                user=request.user
            )
        except PermissionError as exc:
            raise PermissionDenied(detail=str(exc)) from exc
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)}) from exc

        serializer = TicketDetailSerializer(updated_ticket, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def statistics(self, request):
        """
        Get ticket statistics for current user.
        """
        stats = TicketService.get_ticket_statistics(request.user)
        return Response(stats)


class TicketCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ticket categories.
    
    Admins can create/update/delete categories.
    All authenticated users can view categories.
    """
    queryset = TicketCategory.objects.all()
    serializer_class = TicketCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Only admins can modify categories."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class TicketMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ticket messages.
    
    Uses service layer for business logic and access control.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ticket']
    ordering = ['created_at']

    def get_queryset(self):
        """Get messages based on user role using service layer."""
        ticket_id = self.request.query_params.get('ticket')
        return MessageService.get_messages_for_user(
            user=self.request.user,
            ticket_id=ticket_id
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TicketMessageCreateSerializer
        return TicketMessageSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsMessageOwnerOrTicketParticipant()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Create message using service layer."""
        try:
            message = MessageService.create_message(
                user=self.request.user,
                ticket_id=serializer.validated_data['ticket'].id,
                message_content=serializer.validated_data['message'],
            )
            serializer.instance = message
        except PermissionError as exc:
            raise PermissionDenied(detail=str(exc)) from exc
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)}) from exc
