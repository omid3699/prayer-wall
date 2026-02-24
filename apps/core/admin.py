from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """A small base admin for models that inherit from `BaseModel`.

    - Shows UUID and timestamps in `list_display` and `readonly_fields`.
    - Orders by `-created_at` by default.
    """

    list_display = ("id", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)
