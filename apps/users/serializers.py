from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import AnonymousUser, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "created_at",
            "updated_at",
            "is_verified",
            "ip_address",
            "user_agent",
            "is_blocked",
        )
        read_only_fields = (
            "email",
            "created_at",
            "updated_at",
            "is_verified",
            "ip_address",
            "user_agent",
        )

    def get_fields(self):
        """Override get_fields to hide admin-only fields from non-admin users."""
        fields = super().get_fields()

        request = self.context.get("request")
        if request and not request.user.is_superuser:
            for field in ("ip_address", "user_agent", "is_blocked"):
                fields.pop(field)
        return fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for handling user registration."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
        )

    def validate_email(self, value):
        """Ensure email uniqueness in a case-insensitive manner."""
        normalized = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def create(self, validated_data):
        request = self.context.get("request")
        password = validated_data.pop("password")
        ip_address = request.META.get("REMOTE_ADDR") if request else None
        user_agent = request.META.get("HTTP_USER_AGENT", "") if request else ""
        return User.objects.create_user(
            password=password,
            ip_address=ip_address,
            user_agent=user_agent,
            **validated_data,
        )


class AnonymousUserSerializer(serializers.ModelSerializer):
    """Serializer for the AnonymousUser model."""

    class Meta:
        model = AnonymousUser
        fields = (
            "id",
            "display_name",
            "created_at",
            "ip_address",
            "user_agent",
            "is_blocked",
        )
        read_only_fields = ("ip_address", "user_agent")

    def get_fields(self):
        """Override get_fields to include all fields for superusers."""
        fields = super().get_fields()
        request = self.context.get("request")
        if request and not request.user.is_superuser:
            fields.pop("is_blocked")
        return fields


class EmailAuthTokenSerializer(serializers.Serializer):
    """Serializer for authenticating users via email instead of username."""

    email = serializers.EmailField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )
        else:
            msg = _("Must include email and password.")
            raise serializers.ValidationError(msg, code="authorization")

        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        if user.is_blocked:
            msg = _("Your account has been blocked.")
            raise serializers.ValidationError(msg, code="authorization")

        if not user.is_verified:
            msg = _("Please verify your email before logging in.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class EmailVerificationRequestSerializer(serializers.Serializer):
    """Serializer to request email verification."""

    email = serializers.EmailField(label=_("Email"))


class EmailVerificationConfirmSerializer(serializers.Serializer):
    """Serializer to confirm email verification."""

    token = serializers.CharField(label=_("Token"))
