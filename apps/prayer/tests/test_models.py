import pytest
from django.contrib.auth import get_user_model

from apps.prayer.models import PrayerRequest
from apps.users.models import AnonymousUser


User = get_user_model()


@pytest.mark.django_db
class TestPrayerRequestModel:
    def test_create_prayer_request_with_user(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(
            user=user, description="Please pray for my family"
        )
        assert prayer.user == user
        assert prayer.anonymous_user is None
        assert prayer.description == "Please pray for my family"
        assert prayer.is_public is True

    def test_create_prayer_request_with_anonymous_user(self):
        anon = AnonymousUser.objects.create(ip_address="192.168.1.1")
        prayer = PrayerRequest.objects.create(
            anonymous_user=anon, description="Need prayers for health"
        )
        assert prayer.anonymous_user == anon
        assert prayer.user is None
        assert prayer.description == "Need prayers for health"

    def test_requester_returns_user(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(user=user, description="Test")
        assert prayer.requester == user

    def test_requester_returns_anonymous_user(self):
        anon = AnonymousUser.objects.create(ip_address="192.168.1.1")
        prayer = PrayerRequest.objects.create(anonymous_user=anon, description="Test")
        assert prayer.requester == anon

    def test_is_registered_true_for_user(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(user=user, description="Test")
        assert prayer.is_registered is True
        assert prayer.is_anonymous is False

    def test_is_anonymous_true_for_anonymous_user(self):
        anon = AnonymousUser.objects.create(ip_address="192.168.1.1")
        prayer = PrayerRequest.objects.create(anonymous_user=anon, description="Test")
        assert prayer.is_anonymous is True
        assert prayer.is_registered is False

    def test_is_public_defaults_to_true(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(user=user, description="Test")
        assert prayer.is_public is True
        assert prayer.is_approved is False

    def test_is_public_can_be_false(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(
            user=user, description="Private request", is_public=False
        )
        assert prayer.is_public is False

    def test_is_approved_defaults_to_false(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(user=user, description="Test")
        assert prayer.is_approved is False

    def test_is_approved_can_be_true(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(
            user=user, description="Approved request", is_approved=True
        )
        assert prayer.is_approved is True

    def test_str_returns_description(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer = PrayerRequest.objects.create(
            user=user, description="My prayer request"
        )
        assert str(prayer) == "My prayer request"

    def test_related_name_user_prayer_requests(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        PrayerRequest.objects.create(user=user, description="Prayer 1")
        PrayerRequest.objects.create(user=user, description="Prayer 2")
        assert user.prayer_requests.count() == 2

    def test_related_name_anonymous_user_prayer_requests(self):
        anon = AnonymousUser.objects.create(ip_address="192.168.1.1")
        PrayerRequest.objects.create(anonymous_user=anon, description="Prayer 1")
        PrayerRequest.objects.create(anonymous_user=anon, description="Prayer 2")
        assert anon.prayer_requests.count() == 2
