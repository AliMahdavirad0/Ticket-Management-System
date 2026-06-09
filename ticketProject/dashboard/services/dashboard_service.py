from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from tickets.models import Ticket, TicketMessage, TicketCategory
from tickets.services import TicketService, MessageService


class DashboardService:
    """Aggregates ticket-system metrics for role-based dashboard views."""

    RECENT_LIMIT = 5

    @classmethod
    def get_overview(cls, user):
        """Build the main dashboard payload for the authenticated user."""
        tickets_qs = TicketService.get_tickets_for_user(user)
        messages_qs = MessageService.get_messages_for_user(user)

        overview = {
            'user': cls._user_summary(user),
            'tickets': TicketService.get_ticket_statistics(user),
            'messages': {
                'total': messages_qs.count(),
            },
            'recent_tickets': cls._serialize_recent_tickets(tickets_qs),
            'recent_messages': cls._serialize_recent_messages(messages_qs),
        }

        if user.role == 'admin':
            overview['admin'] = cls._admin_metrics()
        elif user.role == 'agent':
            overview['agent'] = cls._agent_metrics(user)
        else:
            overview['customer'] = cls._customer_metrics(user, tickets_qs)

        return overview

    @classmethod
    def get_agent_workload(cls):
        """Agent assignment counts for admin dashboard."""
        agents = (
            User.objects.filter(role='agent')
            .annotate(
                assigned_total=Count('assigned_tickets'),
                open_count=Count(
                    'assigned_tickets',
                    filter=Q(assigned_tickets__status=Ticket.Status.OPEN),
                ),
                in_progress_count=Count(
                    'assigned_tickets',
                    filter=Q(assigned_tickets__status=Ticket.Status.IN_PROGRESS),
                ),
            )
            .order_by('-assigned_total', 'username')
        )

        return [
            {
                'id': agent.id,
                'username': agent.username,
                'email': agent.email,
                'assigned_total': agent.assigned_total,
                'open': agent.open_count,
                'in_progress': agent.in_progress_count,
            }
            for agent in agents
        ]

    @staticmethod
    def _user_summary(user):
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        }

    @classmethod
    def _serialize_recent_tickets(cls, queryset):
        ticket_ids = list(
            queryset.order_by('-updated_at').values_list('pk', flat=True)[: cls.RECENT_LIMIT]
        )
        recent = (
            Ticket.objects.filter(pk__in=ticket_ids)
            .select_related('assigned_agent')
            .order_by('-updated_at')
        )
        return [
            {
                'id': ticket.id,
                'title': ticket.title,
                'status': ticket.status,
                'priority': ticket.priority,
                'assigned_agent': (
                    ticket.assigned_agent.username
                    if ticket.assigned_agent
                    else None
                ),
                'updated_at': ticket.updated_at,
            }
            for ticket in recent
        ]

    @classmethod
    def _serialize_recent_messages(cls, queryset):
        message_ids = list(
            queryset.order_by('-created_at').values_list('pk', flat=True)[: cls.RECENT_LIMIT]
        )
        recent = (
            TicketMessage.objects.filter(pk__in=message_ids)
            .select_related('ticket', 'sender')
            .order_by('-created_at')
        )
        return [
            {
                'id': message.id,
                'ticket_id': message.ticket_id,
                'ticket_title': message.ticket.title,
                'sender': message.sender.username,
                'message': message.message[:120],
                'created_at': message.created_at,
            }
            for message in recent
        ]

    @classmethod
    def _admin_metrics(cls):
        all_tickets = Ticket.objects.all()
        week_ago = timezone.now() - timedelta(days=7)

        by_category = list(
            TicketCategory.objects.annotate(
                ticket_count=Count('ticket')
            ).values('id', 'name', 'ticket_count')
        )

        return {
            'users': {
                'total': User.objects.count(),
                'customers': User.objects.filter(role='customer').count(),
                'agents': User.objects.filter(role='agent').count(),
                'admins': User.objects.filter(role='admin').count(),
            },
            'tickets': {
                'total': all_tickets.count(),
                'unassigned': all_tickets.filter(assigned_agent__isnull=True).count(),
                'created_last_7_days': all_tickets.filter(
                    created_at__gte=week_ago
                ).count(),
                'by_status': {
                    'open': all_tickets.filter(status=Ticket.Status.OPEN).count(),
                    'in_progress': all_tickets.filter(
                        status=Ticket.Status.IN_PROGRESS
                    ).count(),
                    'resolved': all_tickets.filter(
                        status=Ticket.Status.RESOLVED
                    ).count(),
                    'closed': all_tickets.filter(status=Ticket.Status.CLOSED).count(),
                },
                'by_priority': {
                    'low': all_tickets.filter(priority=Ticket.Priority.LOW).count(),
                    'medium': all_tickets.filter(
                        priority=Ticket.Priority.MEDIUM
                    ).count(),
                    'high': all_tickets.filter(priority=Ticket.Priority.HIGH).count(),
                    'critical': all_tickets.filter(
                        priority=Ticket.Priority.CRITICAL
                    ).count(),
                },
            },
            'by_category': by_category,
            'messages': {
                'total': TicketMessage.objects.count(),
            },
        }

    @classmethod
    def _agent_metrics(cls, user):
        assigned = Ticket.objects.filter(assigned_agent=user)
        unassigned_pool = Ticket.objects.filter(assigned_agent__isnull=True)

        return {
            'assigned_to_me': assigned.count(),
            'unassigned_pool': unassigned_pool.count(),
            'needs_attention': assigned.filter(
                status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS],
                priority__in=[Ticket.Priority.HIGH, Ticket.Priority.CRITICAL],
            ).count(),
            'by_status': {
                'open': assigned.filter(status=Ticket.Status.OPEN).count(),
                'in_progress': assigned.filter(
                    status=Ticket.Status.IN_PROGRESS
                ).count(),
                'resolved': assigned.filter(status=Ticket.Status.RESOLVED).count(),
                'closed': assigned.filter(status=Ticket.Status.CLOSED).count(),
            },
        }

    @classmethod
    def _customer_metrics(cls, user, tickets_qs):
        return {
            'open_tickets': tickets_qs.filter(status=Ticket.Status.OPEN).count(),
            'awaiting_response': tickets_qs.filter(
                status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
            ).count(),
            'resolved_or_closed': tickets_qs.filter(
                status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
            ).count(),
        }
