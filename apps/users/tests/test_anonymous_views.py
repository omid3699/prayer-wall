import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import AnonymousToken, AnonymousUser


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAnonymousUserEndpoints:
    def test_create_anonymous_user_mints_token(self, api_client):
        response = api_client.post(
            reverse("users:anonymous-create"),
            {
                "display_name": "Guest",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["display_name"] == "Guest"
        assert "token" in response.data
        assert response.data["token"]

    def test_list_requires_admin(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("users:anonymous-list"))
        assert response.status_code == 403

        anon = AnonymousUser.objects.create(display_name="Guest")
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("users:anonymous-list"))
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert results[0]["id"] == str(anon.id)
        assert "is_blocked" in results[0]

    def test_anonymous_token_view_requires_header(self, api_client):
        response = api_client.post(reverse("users:anonymous-token"), {}, format="json")
        assert response.status_code == 403

    def test_anonymous_token_view_returns_token_info(self, api_client):
        anon_user = AnonymousUser.objects.create(display_name="Guest")
        token = AnonymousToken.create_for_anonymous_user(anon_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.token}")

        response = api_client.post(reverse("users:anonymous-token"), {}, format="json")
        assert response.status_code == 200
        assert response.data["token"] == token.token

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
