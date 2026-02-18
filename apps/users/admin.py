from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AnonymousUser, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin for the custom User model.

    Uses Django's built-in UserAdmin as a base but adjusts list display,
    search fields and fieldsets to match the project's custom fields.
    """

    model = User
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_verified",
        "is_blocked",
        "created_at",
    )
    list_filter = ("is_verified", "is_blocked", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_blocked",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "first_name", "last_name"),
            },
        ),
    )


@admin.register(AnonymousUser)
class AnonymousUserAdmin(admin.ModelAdmin):
    """Admin for the AnonymousUser model.

    Displays IP address, user agent and display name in the admin list view.
    """

    model = AnonymousUser
    list_display = ("id", "display_name", "ip_address", "user_agent", "created_at")
    search_fields = ("display_name", "ip_address", "user_agent")
    ordering = ("-created_at",)
