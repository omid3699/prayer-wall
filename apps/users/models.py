from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel


class User(BaseModel, AbstractUser):
    """Custom user model that extends Django's AbstractUser and BaseModel."""

    email = models.EmailField(unique=True)

    is_verfied = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        """Return the username as string representation."""
        return self.username.__str__()


class AnonymousUser(BaseModel):
    """Model to represent anonymous users with IP and user agent information."""

    display_name = models.CharField(max_length=255, default="Anonymous User")
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)

    def __str__(self) -> str:
        """Return the IP address as string representation."""
        return self.ip_address.__str__()
