from rest_framework import serializers

from .models import AnonymousUser, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "created_at",
            "updated_at",
            "is_verified",
        )
        read_only_fields = ("created_at", "updated_at", "is_verified")

    def get_fields(self):
        """Override get_fields to make email read-only on update."""
        fields = super().get_fields()
        if self.instance:
            fields["email"].read_only = True

        request = self.context.get("request")
        if request and request.user.is_superuser:
            admin_fields = {
                "ip_address": serializers.ReadOnlyField(),
                "user_agent": serializers.ReadOnlyField(),
                "is_blocked": serializers.BooleanField(required=False),
            }
            fields.update(admin_fields)
        return fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for handling user registration."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )

    def validate_email(self, value):
        """Ensure email uniqueness in a case-insensitive manner."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AnonymousUserSerializer(serializers.ModelSerializer):
    """Serializer for the AnonymousUser model."""

    class Meta:
        model = AnonymousUser
        fields = (
            "id",
            "display_name",
            "created_at",
        )

    def get_fields(self):
        """Override get_fields to include all fields for superusers."""
        fields = super().get_fields()
        request = self.context.get("request")
        if request and request.user.is_superuser:
            admin_fields = {
                "ip_address": serializers.CharField(read_only=True),
                "user_agent": serializers.CharField(read_only=True),
                "is_blocked": serializers.BooleanField(required=False),
            }
            fields.update(admin_fields)
        return fields
