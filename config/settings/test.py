from .base import LOGGING


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

LOGGING["root"]["level"] = "WARNING"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
