from rest_framework import serializers


class DashboardUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()


class TicketPriorityStatsSerializer(serializers.Serializer):
    low = serializers.IntegerField()
    medium = serializers.IntegerField()
    high = serializers.IntegerField()
    critical = serializers.IntegerField()


class TicketStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    open = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    resolved = serializers.IntegerField()
    closed = serializers.IntegerField()
    by_priority = TicketPriorityStatsSerializer()


class RecentTicketUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class RecentTicketSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    priority = serializers.CharField()
    user = RecentTicketUserSerializer()
    assigned_agent = RecentTicketUserSerializer(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class RecentMessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ticket_id = serializers.IntegerField()
    ticket_title = serializers.CharField()
    sender = serializers.CharField()
    message = serializers.CharField()
    created_at = serializers.DateTimeField()


class AdminUserStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    customers = serializers.IntegerField()
    agents = serializers.IntegerField()
    admins = serializers.IntegerField()


class AdminTicketStatusStatsSerializer(serializers.Serializer):
    open = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    resolved = serializers.IntegerField()
    closed = serializers.IntegerField()


class AdminGlobalTicketStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    unassigned = serializers.IntegerField()
    created_last_7_days = serializers.IntegerField()
    by_status = AdminTicketStatusStatsSerializer()
    by_priority = TicketPriorityStatsSerializer()


class CategoryTicketCountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    ticket_count = serializers.IntegerField()


class AdminMetricsSerializer(serializers.Serializer):
    users = AdminUserStatsSerializer()
    tickets = AdminGlobalTicketStatsSerializer()
    by_category = CategoryTicketCountSerializer(many=True)
    messages = serializers.DictField(child=serializers.IntegerField())


class AgentMetricsSerializer(serializers.Serializer):
    assigned_to_me = serializers.IntegerField()
    unassigned_pool = serializers.IntegerField()
    needs_attention = serializers.IntegerField()
    by_status = AdminTicketStatusStatsSerializer()


class CustomerMetricsSerializer(serializers.Serializer):
    open_tickets = serializers.IntegerField()
    awaiting_response = serializers.IntegerField()
    resolved_or_closed = serializers.IntegerField()


class DashboardOverviewSerializer(serializers.Serializer):
    user = DashboardUserSerializer()
    tickets = TicketStatsSerializer()
    messages = serializers.DictField(child=serializers.IntegerField())
    recent_tickets = RecentTicketSerializer(many=True)
    recent_messages = RecentMessageSerializer(many=True)
    admin = AdminMetricsSerializer(required=False)
    agent = AgentMetricsSerializer(required=False)
    customer = CustomerMetricsSerializer(required=False)


class AgentWorkloadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    assigned_total = serializers.IntegerField()
    open = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    resolved = serializers.IntegerField()
    closed = serializers.IntegerField()
