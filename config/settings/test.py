"""Test settings."""

from .base import *  # noqa: F403


DEBUG = False

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

LOGGING["root"]["level"] = "WARNING"  # noqa: F405
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
