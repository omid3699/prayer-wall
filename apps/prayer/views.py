from typing import ClassVar

from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Prayer, PrayerRequest
from .serializers import (
    PrayerCreateSerializer,
    PrayerRequestCreateSerializer,
    PrayerRequestSerializer,
    PrayerSerializer,
)


class PrayerRequestList(generics.ListAPIView):
    """List prayer requests visible to the caller.

    Visibility:
    - Anonymous callers see only approved + public requests.
    - Authenticated callers see only approved requests (public and private).
    - Admins can see everything.

    Filtering:
    - Admins may filter by `is_approved`/`is_public`.
    - Non-admins cannot, to avoid confusing/meaningless combinations.
    """

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = PrayerRequestSerializer
    pagination_class = PageNumberPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields: ClassVar[list] = []
    search_fields: ClassVar[list] = ["description"]
    ordering_fields: ClassVar[list] = ["created_at", "updated_at"]
    ordering: ClassVar[list] = ["-created_at"]

    def get_queryset(self):
        qs = PrayerRequest.objects.all().annotate(prayer_count=Count("prayers"))

        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            is_approved = self.request.query_params.get("is_approved")
            if is_approved is not None:
                qs = qs.filter(is_approved=is_approved.lower() == "true")

            is_public = self.request.query_params.get("is_public")
            if is_public is not None:
                qs = qs.filter(is_public=is_public.lower() == "true")

            return qs

        qs = qs.filter(is_approved=True)

        if not user.is_authenticated:
            qs = qs.filter(is_public=True)

        return qs


class PrayerRequestCreate(generics.CreateAPIView):
    """Create a new prayer request."""

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = PrayerRequestCreateSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
            return

        anon_user = getattr(self.request, "anonymous_user", None)
        if not anon_user:
            raise PermissionDenied(
                "Anonymous token is required to create a prayer request."
            )

        serializer.save(anonymous_user=anon_user)


class PrayerRequestDetail(generics.RetrieveAPIView):
    """Retrieve a single prayer request."""

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = PrayerRequestSerializer
    queryset = PrayerRequest.objects.all()
    lookup_field = "id"

    def get_object(self):
        obj = super().get_object()
        if not obj.is_approved and not self._is_owner_or_admin(obj):
            raise PermissionDenied("Prayer request not found.")
        if not obj.is_public and not self._is_owner_or_admin(obj):
            raise PermissionDenied("Prayer request not found.")
        return obj

    def _is_owner_or_admin(self, obj):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser:
            return True
        return obj.user == self.request.user or (
            obj.anonymous_user
            and hasattr(self.request, "anonymous_user")
            and obj.anonymous_user == self.request.anonymous_user
        )


class PrayerRequestUpdate(generics.UpdateAPIView):
    """Update a prayer request."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = PrayerRequestSerializer
    queryset = PrayerRequest.objects.all()
    lookup_field = "id"

    def get_object(self):
        obj = super().get_object()
        if not self._is_owner_or_admin(obj):
            raise PermissionDenied("You can only update your own prayer requests.")
        return obj

    def _is_owner_or_admin(self, obj):
        if self.request.user.is_superuser:
            return True
        return obj.user == self.request.user


class PrayerRequestDelete(generics.DestroyAPIView):
    """Delete a prayer request."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = PrayerRequestSerializer
    queryset = PrayerRequest.objects.all()
    lookup_field = "id"

    def get_object(self):
        obj = super().get_object()
        if not self._is_owner_or_admin(obj):
            raise PermissionDenied("You can only delete your own prayer requests.")
        return obj

    def _is_owner_or_admin(self, obj):
        if self.request.user.is_superuser:
            return True
        return obj.user == self.request.user


class PrayerRequestApprove(generics.UpdateAPIView):
    """Approve a prayer request (admin only)."""

    permission_classes: ClassVar[list] = [IsAuthenticated, IsAdminUser]
    serializer_class = PrayerRequestSerializer
    queryset = PrayerRequest.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_approved = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PrayerList(generics.ListAPIView):
    """List all prayers for a prayer request."""

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = PrayerSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        prayer_request_id = self.kwargs.get("id")
        prayer_request = get_object_or_404(
            PrayerRequest, id=prayer_request_id, is_approved=True
        )
        return Prayer.objects.filter(prayer_request=prayer_request).order_by(
            "-created_at"
        )


class PrayerCreate(generics.CreateAPIView):
    """Create a prayer for a prayer request."""

    permission_classes: ClassVar[list] = [AllowAny]
    serializer_class = PrayerCreateSerializer

    def perform_create(self, serializer):
        prayer_request = get_object_or_404(
            PrayerRequest,
            id=self.kwargs.get("id"),
            is_approved=True,
        )

        if self.request.user.is_authenticated:
            user = self.request.user
            anon_user = None
        else:
            user = None
            anon_user = getattr(self.request, "anonymous_user", None)
            if not anon_user:
                raise PermissionDenied(
                    "Anonymous token is required to pray anonymously."
                )

        try:
            serializer.save(
                user=user, anonymous_user=anon_user, prayer_request=prayer_request
            )
        except IntegrityError:
            raise ValidationError(
                {"non_field_errors": "You have already prayed for this request."}
            ) from None


class PrayerDelete(generics.DestroyAPIView):
    """Delete a prayer."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = PrayerSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Prayer.objects.all()

    def get_object(self):
        obj = super().get_object()
        if not self._is_owner_or_admin(obj):
            raise PermissionDenied("You can only delete your own prayers.")
        return obj

    def _is_owner_or_admin(self, obj):
        if self.request.user.is_superuser:
            return True
        return obj.user == self.request.user


class MyPrayerRequestsList(generics.ListAPIView):
    """List current user's prayer requests."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = PrayerRequestSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return PrayerRequest.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class MyPrayersList(generics.ListAPIView):
    """List prayers made by current user."""

    permission_classes: ClassVar[list] = [IsAuthenticated]
    serializer_class = PrayerSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Prayer.objects.filter(user=self.request.user).order_by("-created_at")
