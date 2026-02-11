from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model with display_name field."""

    list_display = (*UserAdmin.list_display, "display_name")
    fieldsets = (*UserAdmin.fieldsets, ("Profile", {"fields": ("display_name",)}))
    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        ("Profile", {"fields": ("display_name",)}),
    )
