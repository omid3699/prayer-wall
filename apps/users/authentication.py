from __future__ import annotations

from dataclasses import dataclass

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import AnonymousToken, AnonymousUser


class AnonymousUserPrincipal:
    """Lightweight principal used as DRF `request.user` for anonymous auth."""

    is_authenticated = False
    is_anonymous = True
    is_superuser = False

    def __str__(self) -> str:
        """Return a human-readable representation."""
        return "AnonymousUser"


@dataclass(frozen=True)
class AnonymousAuthResult:
    anonymous_user: AnonymousUser
    token: AnonymousToken


class AnonymousTokenAuthentication(BaseAuthentication):
    """Authenticate anonymous users via `Authorization: Token <token>`.

    This is separate from DRF's built-in TokenAuthentication (registered users).
    Views can access the anonymous identity via `request.anonymous_user`.
    """

    keyword = "Token"

    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth:
            return None

        try:
            keyword, token_value = auth.split(" ", 1)
        except ValueError:
            return None

        if keyword != self.keyword:
            return None

        token_value = token_value.strip()
        if not token_value:
            raise AuthenticationFailed("Invalid token header.")

        token = (
            AnonymousToken.objects.select_related("anonymous_user")
            .filter(token=token_value, is_active=True)
            .first()
        )
        if not token:
            raise AuthenticationFailed("Invalid token.")

        if token.expires_at <= timezone.now():
            raise AuthenticationFailed("Token expired.")

        if token.anonymous_user.is_blocked:
            raise AuthenticationFailed("Anonymous user is blocked.")

        request.anonymous_user = token.anonymous_user

        return (
            AnonymousUserPrincipal(),
            AnonymousAuthResult(anonymous_user=token.anonymous_user, token=token),
        )
