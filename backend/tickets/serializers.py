from rest_framework import serializers
from .models import Ticket, TicketCategory, TicketMessage
from accounts.serializers import UserMinimalSerializer


class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = "__all__"


class TicketMessageSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_id', 'message', 'created_at']
        read_only_fields = ['sender', 'created_at']


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    class Meta:
        model = TicketMessage
        fields = ['ticket', 'message']

    def validate_message(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError('Message cannot be empty.')
        return value


class TicketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket lists."""
    user = UserMinimalSerializer(read_only=True)
    assigned_agent = UserMinimalSerializer(read_only=True)
    category = TicketCategorySerializer(read_only=True)
    description = serializers.SerializerMethodField()
    message_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'user',
            'assigned_agent', 'category', 'message_count', 'created_at', 'updated_at'
        ]

    def get_description(self, obj):
        """Return truncated description for list view."""
        desc = obj.description
        if desc and len(desc) > 200:
            return desc[:200] + '...'
        return desc


class TicketDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested relationships."""
    user = UserMinimalSerializer(read_only=True)
    assigned_agent = UserMinimalSerializer(read_only=True)
    category = TicketCategorySerializer(read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'user', 'assigned_agent', 'category',
            'messages', 'created_at', 'updated_at'
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets."""
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category']

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                'Title must be at least 5 characters.'
            )
        return value

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Description must be at least 10 characters.'
            )
        return value


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tickets (limited fields)."""

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category']

    def validate_title(self, value):
        if value is not None and len(value.strip()) < 5:
            raise serializers.ValidationError(
                'Title must be at least 5 characters.'
            )
        return value

    def validate_description(self, value):
        if value is not None and len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Description must be at least 10 characters.'
            )
        return value


class TicketStatusChangeSerializer(serializers.Serializer):
    """Serializer for changing ticket status."""
    status = serializers.ChoiceField(choices=Ticket.Status.choices)


class TicketAssignSerializer(serializers.Serializer):
    """Serializer for assigning agent to ticket."""
    agent_id = serializers.IntegerField()


class TicketPriorityChangeSerializer(serializers.Serializer):
    """Serializer for changing ticket priority."""
    priority = serializers.ChoiceField(choices=Ticket.Priority.choices)
