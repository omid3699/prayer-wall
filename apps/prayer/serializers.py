from rest_framework import serializers

from apps.users.serializers import AnonymousUserSerializer, UserSerializer

from .models import Prayer, PrayerRequest


class PrayerRequestSerializer(serializers.ModelSerializer):
    """Serializer for the PrayerRequest model."""

    prayer_count = serializers.IntegerField(read_only=True)
    user_detail = serializers.SerializerMethodField()
    anonymous_user_detail = serializers.SerializerMethodField()

    class Meta:
        model = PrayerRequest
        fields = (
            "id",
            "user",
            "anonymous_user",
            "user_detail",
            "anonymous_user_detail",
            "description",
            "is_public",
            "is_approved",
            "prayer_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "user",
            "anonymous_user",
            "is_approved",
            "created_at",
            "updated_at",
        )

    def get_fields(self):
        """Override get_fields to hide admin-only fields from non-admin users."""
        fields = super().get_fields()
        request = self.context.get("request")
        if request and not request.user.is_superuser:
            fields.pop("is_approved", None)
        return fields

    def get_user_detail(self, obj):
        """Return user detail if requester is a registered user."""
        if obj.user:
            return UserSerializer(obj.user, context=self.context).data
        return None

    def get_anonymous_user_detail(self, obj):
        """Return anonymous user detail if requester is anonymous."""
        if obj.anonymous_user:
            return AnonymousUserSerializer(
                obj.anonymous_user, context=self.context
            ).data
        return None

    def to_representation(self, instance):
        """Override to add prayer_count."""
        data = super().to_representation(instance)
        data["prayer_count"] = instance.prayers.count()
        return data


class PrayerRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PrayerRequest."""

    class Meta:
        model = PrayerRequest
        fields = (
            "description",
            "is_public",
        )


class PrayerSerializer(serializers.ModelSerializer):
    """Serializer for the Prayer model."""

    user_detail = serializers.SerializerMethodField()
    anonymous_user_detail = serializers.SerializerMethodField()

    class Meta:
        model = Prayer
        fields = (
            "id",
            "user",
            "anonymous_user",
            "user_detail",
            "anonymous_user_detail",
            "prayer_request",
            "created_at",
        )
        read_only_fields = (
            "user",
            "anonymous_user",
            "prayer_request",
            "created_at",
        )

    def get_user_detail(self, obj):
        """Return user detail if prayer is from a registered user."""
        if obj.user:
            return UserSerializer(obj.user, context=self.context).data
        return None

    def get_anonymous_user_detail(self, obj):
        """Return anonymous user detail if prayer is from anonymous."""
        if obj.anonymous_user:
            return AnonymousUserSerializer(
                obj.anonymous_user, context=self.context
            ).data
        return None


class PrayerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Prayer."""

    class Meta:
        model = Prayer
        fields = ("prayer_request",)
