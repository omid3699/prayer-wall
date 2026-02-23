import pytest
from django.contrib.auth import get_user_model

from apps.prayer.models import Prayer, PrayerRequest
from apps.prayer.serializers import (
    PrayerCreateSerializer,
    PrayerRequestCreateSerializer,
    PrayerRequestSerializer,
    PrayerSerializer,
)
from apps.users.models import AnonymousUser


User = get_user_model()


@pytest.mark.django_db
class TestPrayerRequestSerializer:
    def test_serialize_prayer_request_with_user(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Please pray for my family"
        )
        serializer = PrayerRequestSerializer(prayer_request)
        data = serializer.data

        assert data["description"] == "Please pray for my family"
        assert data["user"] == user.id
        assert data["anonymous_user"] is None
        assert data["prayer_count"] == 0
        assert data["is_public"] is True

    def test_serialize_prayer_request_with_anonymous_user(self):
        anon = AnonymousUser.objects.create(ip_address="192.168.1.1")
        prayer_request = PrayerRequest.objects.create(
            anonymous_user=anon, description="Need prayers"
        )
        serializer = PrayerRequestSerializer(prayer_request)
        data = serializer.data

        assert data["description"] == "Need prayers"
        assert data["anonymous_user"] == anon.id
        assert data["user"] is None
        assert data["prayer_count"] == 0

    def test_serialize_includes_user_detail(self):
        user = User.objects.create_user(
            email="user@example.com", password="pass1234", first_name="John"
        )
        prayer_request = PrayerRequest.objects.create(user=user, description="Test")
        serializer = PrayerRequestSerializer(prayer_request)
        data = serializer.data

        assert data["user_detail"]["email"] == "user@example.com"
        assert data["user_detail"]["first_name"] == "John"

    def test_serialize_includes_anonymous_user_detail(self):
        anon = AnonymousUser.objects.create(
            ip_address="192.168.1.1", display_name="Anonymous User"
        )
        prayer_request = PrayerRequest.objects.create(
            anonymous_user=anon, description="Test"
        )
        serializer = PrayerRequestSerializer(prayer_request)
        data = serializer.data

        assert data["anonymous_user_detail"]["display_name"] == "Anonymous User"
        assert data["anonymous_user_detail"]["ip_address"] == "192.168.1.1"

    def test_serialize_includes_prayer_count(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(user=user, description="Test")
        Prayer.objects.create(
            user=User.objects.create_user(
                email="prayer1@example.com", password="pass1234"
            ),
            prayer_request=prayer_request,
        )
        Prayer.objects.create(
            user=User.objects.create_user(
                email="prayer2@example.com", password="pass1234"
            ),
            prayer_request=prayer_request,
        )

        serializer = PrayerRequestSerializer(prayer_request)
        data = serializer.data

        assert data["prayer_count"] == 2


@pytest.mark.django_db
class TestPrayerRequestCreateSerializer:
    def test_create_prayer_request(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        data = {"description": "Please pray for me", "is_public": True}
        serializer = PrayerRequestCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        prayer_request = serializer.save(user=user)

        assert prayer_request.user == user
        assert prayer_request.description == "Please pray for me"
        assert prayer_request.is_public is True

    def test_create_prayer_request_validation(self):
        data = {"description": "", "is_public": True}
        serializer = PrayerRequestCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "description" in serializer.errors


@pytest.mark.django_db
class TestPrayerSerializer:
    def test_serialize_prayer_with_user(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(user=user, description="Test")
        prayer = Prayer.objects.create(user=user, prayer_request=prayer_request)

        serializer = PrayerSerializer(prayer)
        data = serializer.data

        assert data["user"] == user.id
        assert data["anonymous_user"] is None
        assert data["prayer_request"] == prayer_request.id

    def test_serialize_prayer_with_anonymous_user(self):
        anon = AnonymousUser.objects.create(ip_address="192.168.1.1")
        prayer_request = PrayerRequest.objects.create(
            anonymous_user=anon, description="Test"
        )
        prayer = Prayer.objects.create(
            anonymous_user=anon, prayer_request=prayer_request
        )

        serializer = PrayerSerializer(prayer)
        data = serializer.data

        assert data["anonymous_user"] == anon.id
        assert data["user"] is None


@pytest.mark.django_db
class TestPrayerCreateSerializer:
    def test_create_prayer(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(user=user, description="Test")
        data = {"prayer_request": str(prayer_request.id)}
        serializer = PrayerCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        prayer = serializer.save(user=user)

        assert prayer.user == user
        assert prayer.prayer_request == prayer_request

    def test_create_prayer_validation(self):
        data = {"prayer_request": "invalid-uuid"}
        serializer = PrayerCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "prayer_request" in serializer.errors
