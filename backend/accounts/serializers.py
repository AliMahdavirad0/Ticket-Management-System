from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': False, 'default': 'customer'},
        }

    def validate_role(self, value):
        if value and value != 'customer':
            raise serializers.ValidationError(
                'Public registration only allows the customer role.'
            )
        return value or 'customer'

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password': ["Password fields didn't match."]}
            )
        attrs.setdefault('role', 'customer')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role', 'customer')
        
        user = User.objects.create_user(**validated_data)
        user.role = role
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer with statistics."""
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'date_joined', 'statistics']
        read_only_fields = ['id', 'date_joined']

    def get_statistics(self, obj):
        if obj.role == 'customer':
            return {
                'total_tickets': obj.tickets.count(),
                'open_tickets': obj.tickets.filter(status='OPEN').count(),
                'resolved_tickets': obj.tickets.filter(status='RESOLVED').count(),
            }
        elif obj.role == 'agent':
            return {
                'assigned_tickets': obj.assigned_tickets.count(),
                'open_assigned': obj.assigned_tickets.filter(status='OPEN').count(),
                'resolved_assigned': obj.assigned_tickets.filter(status='RESOLVED').count(),
            }
        return {}


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for nested serialization and login response."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']
        read_only_fields = fields


class AvailableAgentSerializer(serializers.ModelSerializer):
    """Serializer for available agents with assigned count."""
    assigned_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'assigned_count']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user role (admin only)."""
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {'new_password': ["Password fields didn't match."]}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {'old_password': ['Old password is incorrect.']}
            )
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
