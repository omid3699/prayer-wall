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
        "username",
        "email",
        "is_verfied",
        "is_blocked",
        "created_at",
    )
    list_filter = ("is_verfied", "is_blocked", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_verfied",
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
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


class AnonymousUserAdmin(admin.ModelAdmin):
    """Admin for the AnonymousUser model.

    Displays IP address, user agent and display name in the admin list view.
    """

    model = AnonymousUser
    list_display = ("id", "display_name", "ip_address", "user_agent", "created_at")
    search_fields = ("display_name", "ip_address", "user_agent")
    ordering = ("-created_at",)
