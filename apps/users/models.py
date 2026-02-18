from typing import ClassVar

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel


class UserManager(BaseUserManager):
    """Custom manager that uses email as the unique identifier."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email address must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class User(BaseModel, AbstractUser):
    """Custom user model that extends Django's AbstractUser and BaseModel."""

    username = None
    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects = UserManager()

    def __str__(self) -> str:
        """Return the email as string representation."""
        return self.email

    @property
    def display_name(self) -> str:
        """Return the display name for the user."""
        return self.get_full_name() or self.email


class AnonymousUser(BaseModel):
    """Model to represent anonymous users with IP and user agent information."""

    display_name = models.CharField(max_length=255, default="Anonymous User")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return the IP address as string representation."""
        return self.ip_address or self.display_name
