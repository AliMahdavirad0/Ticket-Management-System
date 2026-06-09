from rest_framework import serializers
from .models import Ticket, TicketCategory, TicketMessage


class UserMinimalSerializer(serializers.Serializer):
    """Minimal user representation for nested serialization."""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)


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
    category_name = serializers.CharField(source='category.name', read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'status', 'priority', 'user', 'assigned_agent',
            'category', 'category_name', 'message_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'assigned_agent', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count() if hasattr(obj, 'messages') else 0


class TicketDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested relationships."""
    user = UserMinimalSerializer(read_only=True)
    assigned_agent = UserMinimalSerializer(read_only=True)
    category_detail = TicketCategorySerializer(source='category', read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    recent_messages = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'user', 'assigned_agent', 'category', 'category_detail',
            'messages', 'recent_messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'assigned_agent', 'created_at', 'updated_at']

    def get_recent_messages(self, obj):
        """Get last 5 messages for quick preview."""
        recent = obj.messages.all()[:5] if hasattr(obj, 'messages') else []
        return TicketMessageSerializer(recent, many=True).data


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


# Legacy serializer for backward compatibility
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ['user', 'assigned_agent', 'created_at', 'updated_at']
