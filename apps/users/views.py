from typing import ClassVar

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import AnonymousToken, AnonymousUser, EmailVerificationToken, User
from .serializers import (
    AnonymousTokenSerializer,
    AnonymousUserSerializer,
    AnonymousUserWithTokenSerializer,
    EmailAuthTokenSerializer,
    EmailVerificationConfirmSerializer,
    EmailVerificationRequestSerializer,
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

        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins may view other users.")
        return get_object_or_404(User, id=user_id)


class UserRegister(generics.CreateAPIView):
    """Create a new user."""

    serializer_class = UserRegistrationSerializer
    throttle_scope = "registration"


class UserList(generics.ListAPIView):
    """List all users, restricted to admins."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class UserUpdate(generics.UpdateAPIView):
    """Update user details."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Return request user; only admins may target other users."""
        user_id = self.kwargs.get("id")
        if not user_id:
            return self.request.user

        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins may update other users.")
        return get_object_or_404(User, id=user_id)


class UserDelete(generics.DestroyAPIView):
    """Delete user."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Return request user; only admins may delete arbitrary users."""
        user_id = self.kwargs.get("id")
        if not user_id:
            return self.request.user

        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins may delete other users.")
        return get_object_or_404(User, id=user_id)


class AnonymousUserCreate(generics.CreateAPIView):
    """Create a new anonymous user and mint a token."""

    serializer_class = AnonymousUserSerializer
    throttle_scope = "anonymous-create"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save(
            ip_address=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )

        token = AnonymousToken.create_for_anonymous_user(instance)

        response_data = AnonymousUserWithTokenSerializer(
            instance, context={"request": request}
        ).data
        response_data["token"] = token.token
        response_data["token_expires_at"] = token.expires_at

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class AnonymousUserList(generics.ListAPIView):
    """List all anonymous users (admin only)."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    queryset = AnonymousUser.objects.all()
    serializer_class = AnonymousUserSerializer
    pagination_class = PageNumberPagination


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
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context={"request": request}).data
        return Response({"token": token.key, "user": user_data})


class EmailVerificationRequest(generics.GenericAPIView):
    """Request email verification link."""

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = EmailVerificationRequestSerializer
    throttle_scope = "verification"

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()

        if not user:
            return Response(
                {"detail": "If the email exists, a verification link will be sent."},
                status=status.HTTP_200_OK,
            )

        if user.is_verified:
            return Response(
                {"detail": "This email is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        EmailVerificationToken.create_for_user(user)
        return Response(
            {"detail": "If the email exists, a verification link will be sent."},
            status=status.HTTP_200_OK,
        )


class EmailVerificationConfirm(generics.GenericAPIView):
    """Confirm email verification."""

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = EmailVerificationConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_value = serializer.validated_data["token"]
        token = EmailVerificationToken.objects.filter(token=token_value).first()

        if not token:
            raise ValidationError({"token": "Invalid verification token."})

        if not token.is_valid():
            raise ValidationError(
                {"token": "Verification token has expired or been used."}
            )

        user = token.user
        user.is_verified = True
        user.save()
        token.is_used = True
        token.save()

        return Response(
            {"detail": "Email verified successfully."}, status=status.HTTP_200_OK
        )


class AnonymousTokenView(generics.GenericAPIView):
    """Return the current anonymous token.

    New flow: anonymous identity is established by minting a token (typically via
    `AnonymousUserCreate`). Subsequent anonymous requests must send:

        Authorization: Token <anonymous-token>

    This endpoint simply returns the token info when a valid anonymous token is
    provided.
    """

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = AnonymousTokenSerializer

    def post(self, request, *args, **kwargs):
        auth = request.auth
        if not auth or not hasattr(auth, "token"):
            raise PermissionDenied(
                "Anonymous token is required in Authorization header."
            )

        serializer = AnonymousTokenSerializer(auth.token)
        return Response(serializer.data, status=status.HTTP_200_OK)
