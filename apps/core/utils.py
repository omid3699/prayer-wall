"""Small utilities used across the project by simple, well-tested helpers.

Keep this module minimal: parse helpers and tiny helpers that don't depend on
models to keep import cost low.
"""

import datetime

from django.utils import timezone


def now_utc() -> datetime.datetime:
    """Return timezone-aware UTC now using Django's timezone utilities."""
    return timezone.now()
