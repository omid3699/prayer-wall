import uuid

from django.test import TestCase

from apps.core import utils


class UtilsTests(TestCase):
    def test_now_utc_returns_datetime(self):
        n = utils.now_utc()
        assert hasattr(n, "isoformat")
