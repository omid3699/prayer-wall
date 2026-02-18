import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError


User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(email="test@example.com", password="pass1234")
        assert user.email == "test@example.com"
        assert user.check_password("pass1234")

    def test_str_returns_email(self):
        user = User.objects.create_user(email="str@example.com", password="pass1234")
        assert str(user) == "str@example.com"

    def test_email_unique_constraint(self):
        User.objects.create_user(email="unique@example.com", password="pass1234")
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="unique@example.com", password="pass1234")

    def test_default_flags(self):
        user = User.objects.create_user(email="flag@example.com", password="pass1234")
        assert user.is_verified is False
        assert user.is_blocked is False

    def test_required_fields(self):
        user = User.objects.create_user(
            email="inherit@example.com", password="pass1234"
        )
        assert hasattr(user, "password")
        assert hasattr(user, "email")
        assert hasattr(user, "is_active")
        assert hasattr(user, "is_staff")
