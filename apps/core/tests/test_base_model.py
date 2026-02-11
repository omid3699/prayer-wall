from django.test import TestCase

from apps.core.models import BaseModel


class _TmpModel(BaseModel):
    class Meta(BaseModel.Meta):
        # Make this temporary model concrete for testing
        app_label = "core"


class BaseModelTests(TestCase):
    def test_str_returns_uuid_when_no_name(self):
        obj = _TmpModel()
        # str should not raise and should contain a hyphen from UUID
        s = str(obj)
        assert "-" in s
