import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.prayer.models import Prayer, PrayerRequest
from apps.users.models import AnonymousUser


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestPrayerRequestListView:
    def test_list_returns_approved_public_requests(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        PrayerRequest.objects.create(
            user=user, description="Public prayer", is_approved=True, is_public=True
        )
        PrayerRequest.objects.create(
            user=user, description="Private prayer", is_approved=True, is_public=False
        )
        PrayerRequest.objects.create(
            user=user,
            description="Unapproved prayer",
            is_approved=False,
            is_public=True,
        )

        response = api_client.get(reverse("prayers:list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["description"] == "Public prayer"

    def test_list_empty(self, api_client):
        response = api_client.get(reverse("prayers:list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_search_by_description(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        PrayerRequest.objects.create(
            user=user, description="Pray for health", is_approved=True, is_public=True
        )
        PrayerRequest.objects.create(
            user=user, description="Pray for peace", is_approved=True, is_public=True
        )
        PrayerRequest.objects.create(
            user=user, description="Thank you Lord", is_approved=True, is_public=True
        )

        response = api_client.get(reverse("prayers:list"), {"search": "health"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["description"] == "Pray for health"

    def test_search_no_results(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        PrayerRequest.objects.create(
            user=user, description="Pray for health", is_approved=True, is_public=True
        )

        response = api_client.get(reverse("prayers:list"), {"search": "nonexistent"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_ordering_by_created_at_ascending(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer1 = PrayerRequest.objects.create(
            user=user, description="First prayer", is_approved=True, is_public=True
        )
        prayer2 = PrayerRequest.objects.create(
            user=user, description="Second prayer", is_approved=True, is_public=True
        )

        response = api_client.get(reverse("prayers:list"), {"ordering": "created_at"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["description"] == "First prayer"
        assert response.data["results"][1]["description"] == "Second prayer"

    def test_ordering_by_created_at_descending(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer1 = PrayerRequest.objects.create(
            user=user, description="First prayer", is_approved=True, is_public=True
        )
        prayer2 = PrayerRequest.objects.create(
            user=user, description="Second prayer", is_approved=True, is_public=True
        )

        response = api_client.get(reverse("prayers:list"), {"ordering": "-created_at"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["description"] == "Second prayer"
        assert response.data["results"][1]["description"] == "First prayer"


@pytest.mark.django_db
class TestPrayerRequestCreateView:
    def test_create_as_authenticated_user(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)

        response = api_client.post(
            reverse("prayers:create"),
            {"description": "Please pray for me", "is_public": True},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        prayer_request = PrayerRequest.objects.first()
        assert prayer_request.user == user
        assert prayer_request.description == "Please pray for me"

    def test_create_as_anonymous_user(self, api_client):
        response = api_client.post(
            reverse("prayers:create"),
            {"description": "Anonymous prayer request", "is_public": True},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        prayer_request = PrayerRequest.objects.first()
        assert prayer_request.anonymous_user is not None
        assert prayer_request.description == "Anonymous prayer request"

    def test_create_validation_error(self, api_client):
        response = api_client.post(
            reverse("prayers:create"),
            {"description": "", "is_public": True},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "description" in response.data


@pytest.mark.django_db
class TestPrayerRequestDetailView:
    def test_detail_approved_public_request(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Test prayer", is_approved=True, is_public=True
        )

        response = api_client.get(
            reverse("prayers:detail", kwargs={"id": prayer_request.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == "Test prayer"

    def test_detail_unapproved_not_found(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Test prayer", is_approved=False, is_public=True
        )

        response = api_client.get(
            reverse("prayers:detail", kwargs={"id": prayer_request.id})
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPrayerRequestUpdateView:
    def test_update_own_request(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Original description", is_approved=True
        )

        response = api_client.patch(
            reverse("prayers:update", kwargs={"id": prayer_request.id}),
            {"description": "Updated description"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        prayer_request.refresh_from_db()
        assert prayer_request.description == "Updated description"

    def test_update_other_user_forbidden(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=other, description="Other's prayer", is_approved=True
        )

        response = api_client.patch(
            reverse("prayers:update", kwargs={"id": prayer_request.id}),
            {"description": "Hacked!"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPrayerRequestDeleteView:
    def test_delete_own_request(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="To be deleted", is_approved=True
        )

        response = api_client.delete(
            reverse("prayers:delete", kwargs={"id": prayer_request.id})
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not PrayerRequest.objects.filter(id=prayer_request.id).exists()


@pytest.mark.django_db
class TestPrayerRequestApproveView:
    def test_approve_as_admin(self, api_client):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        api_client.force_authenticate(user=admin)
        prayer_request = PrayerRequest.objects.create(
            user=admin, description="Needs approval", is_approved=False
        )

        response = api_client.patch(
            reverse("prayers:approve", kwargs={"id": prayer_request.id}),
            {"is_approved": True},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        prayer_request.refresh_from_db()
        assert prayer_request.is_approved is True

    def test_approve_as_non_admin_forbidden(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Needs approval", is_approved=False
        )

        response = api_client.post(
            reverse("prayers:approve", kwargs={"id": prayer_request.id})
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPrayerCreateView:
    def test_pray_as_authenticated_user(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Pray for me", is_approved=True
        )

        response = api_client.post(
            reverse("prayers:pray", kwargs={"id": prayer_request.id}),
            {"prayer_request": str(prayer_request.id)},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert prayer_request.prayers.count() == 1

    def test_pray_as_anonymous_user(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Pray for me", is_approved=True
        )

        response = api_client.post(
            reverse("prayers:pray", kwargs={"id": prayer_request.id}),
            {"prayer_request": str(prayer_request.id)},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert prayer_request.prayers.count() == 1
        assert prayer_request.prayers.first().anonymous_user is not None

    def test_cannot_pray_twice(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Pray for me", is_approved=True
        )
        Prayer.objects.create(user=user, prayer_request=prayer_request)

        response = api_client.post(
            reverse("prayers:pray", kwargs={"id": prayer_request.id})
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_pray_for_unapproved_request(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Not approved", is_approved=False
        )

        response = api_client.post(
            reverse("prayers:pray", kwargs={"id": prayer_request.id}),
            {"prayer_request": str(prayer_request.id)},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPrayerListView:
    def test_list_prayers_for_request(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Pray for me", is_approved=True
        )
        Prayer.objects.create(
            user=User.objects.create_user(
                email="prayer1@example.com", password="pass1234"
            ),
            prayer_request=prayer_request,
        )
        Prayer.objects.create(
            user=User.objects.create_user(
                email="prayer2@example.com", password="pass1234"
            ),
            prayer_request=prayer_request,
        )

        response = api_client.get(
            reverse("prayers:prayer-list", kwargs={"id": prayer_request.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


@pytest.mark.django_db
class TestPrayerDeleteView:
    def test_delete_own_prayer(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Pray for me", is_approved=True
        )
        prayer = Prayer.objects.create(user=user, prayer_request=prayer_request)

        response = api_client.delete(
            reverse("prayers:prayer-delete", kwargs={"id": prayer.id})
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Prayer.objects.filter(id=prayer.id).exists()

    def test_cannot_delete_other_prayer(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        prayer_request = PrayerRequest.objects.create(
            user=user, description="Pray for me", is_approved=True
        )
        prayer = Prayer.objects.create(user=other, prayer_request=prayer_request)

        response = api_client.delete(
            reverse("prayers:prayer-delete", kwargs={"id": prayer.id})
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
