import uuid

import pytest

from apps.prayer.models import PrayerRequest


@pytest.mark.django_db
class TestBaseModel:
    def test_id_is_uuid_primary_key(self):
        obj = PrayerRequest.objects.create(description="test", is_public=True)
        assert isinstance(obj.id, uuid.UUID)

    def test_timestamps_are_set(self):
        obj = PrayerRequest.objects.create(description="test", is_public=True)
        assert obj.created_at is not None
        assert obj.updated_at is not None
