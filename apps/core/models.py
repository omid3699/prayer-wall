import typing
import uuid

from django.db import models


class BaseModel(models.Model):
    """Abstract base model that provides a UUID primary key and timestamp fields.

    Models that inherit from this class will have a `uuid` field as the primary
    key, along with `created_at` and `updated_at` timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        """Meta options.

        Meta options for BaseModel marking it as abstract and providing a
        sensible default ordering.
        """

        abstract = True
        ordering: typing.ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        """Human-friendly representation.

        If a model defines a `name` or `title` attribute/field, prefer that; fall
        back to the UUID.
        """
        name = getattr(self, "name", None) or getattr(self, "title", None)
        return str(name) if name is not None else str(self.uuid)
