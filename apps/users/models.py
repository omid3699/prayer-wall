from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel


class User(BaseModel, AbstractUser):
    """Custom user model that extends Django's AbstractUser and BaseModel."""

    email = models.EmailField(unique=True)

    is_verfied = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return the username as string representation."""
        return self.username.__str__()
