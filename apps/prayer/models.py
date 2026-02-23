from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel
from apps.users.models import AnonymousUser, User


class PrayerRequest(BaseModel):
    """Model representing a prayer request."""

    ## TODO: Add AI generated title for the prayer request based on the description.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="prayer_requests",
    )
    anonymous_user = models.ForeignKey(
        AnonymousUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="prayer_requests",
    )
    description = models.TextField(
        max_length=1000,
        help_text="Description of the prayer request",
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether the prayer request is public or private",
    )
    # TODO: Add AI generated tags for the prayer request based on the description.
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether the prayer request has been approved by an admin",
    )
    ## TODO: Review the prayer requests autmatically using AI and approve them if they are appropriate.

    class Meta:
        pass

    def __str__(self) -> str:
        """Return the description as string representation."""
        return self.description

    def clean(self):
        if not bool(self.user) ^ bool(self.anonymous_user):
            raise ValidationError(
                "Prayer request must have either a user or anonymous user, not both and not neither."
            )

    @property
    def requester(self):
        """Return the user or anonymous user who made this request."""
        return self.user or self.anonymous_user

    @property
    def is_anonymous(self) -> bool:
        """Return True if this request was made by an anonymous user."""
        return self.anonymous_user is not None

    @property
    def is_registered(self) -> bool:
        """Return True if this request was made by a registered user."""
        return self.user is not None
