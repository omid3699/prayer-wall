import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.users.serializers import UserRegistrationSerializer, UserSerializer


User = get_user_model()


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    def test_registration_success(self):
        serializer = UserRegistrationSerializer(
            data={
                "email": "user@example.com",
                "password": "strongpass",
                "first_name": "First",
                "last_name": "Last",
            }
        )
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.email == "user@example.com"
        assert user.check_password("strongpass")

    def test_registration_duplicate_email(self):
        User.objects.create_user(email="user@example.com", password="pass1234")
        serializer = UserRegistrationSerializer(
            data={
                "email": "user@example.com",
                "password": "anotherpass",
            }
        )
        assert serializer.is_valid() is False
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestUserSerializer:
    def test_read_only_email(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        serializer = UserSerializer(
            instance=user,
            data={"email": "new@example.com", "first_name": "Test"},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.email == "user@example.com"
        assert user.first_name == "Test"

    def test_admin_fields_included(self, request_factory):
        admin = User.objects.create_superuser(email="admin@example.com", password="pass1234")
        request = request_factory.get("/users/me/")
        request.user = admin
        serializer = UserSerializer(instance=admin, context={"request": request})
        assert "ip_address" in serializer.data
        assert "user_agent" in serializer.data
