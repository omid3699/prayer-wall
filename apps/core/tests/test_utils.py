from django.test import TestCase

from apps.core import utils


class UtilsTests(TestCase):
    """Test cases for core utility functions."""

    def test_now_utc_returns_datetime(self):
        """Test that now_utc returns a datetime object."""
        n = utils.now_utc()
        assert hasattr(n, "isoformat")
