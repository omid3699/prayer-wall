import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import AnonymousUser


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAnonymousUserEndpoints:
    def test_create_anonymous_user(self, api_client):
        response = api_client.post(
            reverse("users:anonymous-create"),
            {"display_name": "Guest"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["display_name"] == "Guest"

    def test_list_requires_admin(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("users:anonymous-list"))
        assert response.status_code == 403

        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("users:anonymous-list"))
        assert response.status_code == 200

    def test_delete_requires_admin(self, api_client):
        anon = AnonymousUser.objects.create(display_name="Guest")
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.delete(
            reverse("users:anonymous-delete", kwargs={"id": anon.id})
        )
        assert response.status_code == 403

        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        api_client.force_authenticate(user=admin)
        response = api_client.delete(
            reverse("users:anonymous-delete", kwargs={"id": anon.id})
        )
        assert response.status_code == 204
