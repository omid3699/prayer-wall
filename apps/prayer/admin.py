from django.contrib import admin

from .models import Prayer, PrayerRequest


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    """Admin for the PrayerRequest model."""

    model = PrayerRequest
    list_display = (
        "id",
        "description",
        "user",
        "anonymous_user",
        "is_public",
        "is_approved",
        "created_at",
    )
    list_filter = ("is_public", "is_approved", "created_at")
    search_fields = ("description", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Prayer)
class PrayerAdmin(admin.ModelAdmin):
    """Admin for the Prayer model."""

    model = Prayer
    list_display = (
        "id",
        "user",
        "anonymous_user",
        "prayer_request",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__email", "prayer_request__description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
