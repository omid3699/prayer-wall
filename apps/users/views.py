from typing import ClassVar

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import AnonymousUser, User
from .serializers import (
    AnonymousUserSerializer,
    EmailAuthTokenSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserDetail(generics.RetrieveAPIView):
    """Return details for the request user or for a specific user id."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Return request user or the user for the 'id' URL kwarg."""
        user_id = self.kwargs.get("id")
        if not user_id:
            return self.request.user

        if not self.request.user.is_superuser and self.request.user.id != user_id:
            raise PermissionDenied("You do not have permission to view this user.")
        return get_object_or_404(User, id=user_id)


class UserRegister(generics.CreateAPIView):
    """Create a new user."""

    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        serializer.save(
            ip_address=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )


class UserList(generics.ListAPIView):
    """List all users, restricted to admins."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdate(generics.UpdateAPIView):
    """Update user details."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Return request user, admins may target other users."""
        user_id = self.kwargs.get("id")
        if not user_id:
            return self.request.user

        if not self.request.user.is_superuser and self.request.user.id != user_id:
            raise PermissionDenied("You do not have permission to update this user.")
        return get_object_or_404(User, id=user_id)


class UserDelete(generics.DestroyAPIView):
    """Delete user."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Return request user; admins may delete arbitrary users."""
        user_id = self.kwargs.get("id")
        if not user_id:
            return self.request.user

        if not self.request.user.is_superuser and self.request.user.id != user_id:
            raise PermissionDenied("You do not have permission to delete this user.")
        return get_object_or_404(User, id=user_id)


class AnonymousUserCreate(generics.CreateAPIView):
    """Create a new anonymous user."""

    serializer_class = AnonymousUserSerializer

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data["ip_address"] = self.request.META.get("REMOTE_ADDR")
        validated_data["user_agent"] = self.request.META.get("HTTP_USER_AGENT", "")
        serializer.save(**validated_data)


class AnonymousUserList(generics.ListAPIView):
    """List all anonymous users (admin only)."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    queryset = AnonymousUser.objects.all()
    serializer_class = AnonymousUserSerializer


class AnonymousUserDelete(generics.DestroyAPIView):
    """Delete anonymous user."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    serializer_class = AnonymousUserSerializer

    def get_object(self):
        anon_id = self.kwargs.get("id")
        if not anon_id:
            raise PermissionDenied("Anonymous user id is required.")
        return get_object_or_404(AnonymousUser, id=anon_id)


class AnonymousUserDetail(generics.RetrieveAPIView):
    """Return details for a specific anonymous user id."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    serializer_class = AnonymousUserSerializer

    def get_object(self):
        anon_id = self.kwargs.get("id")
        return get_object_or_404(AnonymousUser, id=anon_id)


class EmailObtainAuthToken(ObtainAuthToken):
    """Custom auth token view that works with email-only users."""

    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
