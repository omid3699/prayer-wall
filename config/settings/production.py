import os

from .base import LOGGING, SECRET_KEY


# Override as needed
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()
]
DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

LOGGING["root"]["level"] = "INFO"

# Assertions
if DEBUG:
    raise RuntimeError("DEBUG must be False in production settings")
if SECRET_KEY in ("please-change-me", ""):
    raise RuntimeError(
        "SECRET_KEY must be set in production and must not be the default placeholder"
    )
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must be set in production")
