import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass1234"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("pass1234")

    def test_str_returns_username(self):
        user = User.objects.create_user(
            username="struser", email="str@example.com", password="pass1234"
        )
        assert str(user) == "struser"

    def test_email_unique_constraint(self):
        User.objects.create_user(
            username="user1", email="unique@example.com", password="pass1234"
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                username="user2", email="unique@example.com", password="pass1234"
            )

    def test_default_flags(self):
        user = User.objects.create_user(
            username="flaguser", email="flag@example.com", password="pass1234"
        )
        assert user.is_verified is False
        assert user.is_blocked is False

    def test_inherited_fields(self):
        user = User.objects.create_user(
            username="inherituser", email="inherit@example.com", password="pass1234"
        )
        assert hasattr(user, "username")
        assert hasattr(user, "password")
        assert hasattr(user, "email")
        assert hasattr(user, "is_active")
        assert hasattr(user, "is_staff")
