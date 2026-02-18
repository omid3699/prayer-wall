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
            "display_name",
            "created_at",
            "updated_at",
            "is_verified",
        )
        read_only_fields = ("email", "created_at", "updated_at", "is_verified")

    def get_fields(self):
        """Override get_fields to include admin-only fields."""
        fields = super().get_fields()

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
        return User.objects.create_user(password=password, **validated_data)


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

        attrs["user"] = user
        return attrs
