import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestUserEndpoints:
    def test_register_user(self, api_client):
        response = api_client.post(
            reverse("users:register"),
            {
                "email": "user@example.com",
                "password": "pass1234",
                "first_name": "First",
                "last_name": "Last",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["email"] == "user@example.com"

    def test_user_detail_self(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("users:me"))
        assert response.status_code == 200
        assert response.data["email"] == "user@example.com"
        assert "ip_address" not in response.data

    def test_user_detail_admin_can_view_other(self, api_client):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        other = User.objects.create_user(
            email="other@example.com",
            password="pass1234",
            ip_address="1.1.1.1",
        )
        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("users:detail", kwargs={"id": other.id}))
        assert response.status_code == 200
        assert response.data["email"] == "other@example.com"
        assert response.data["ip_address"] == "1.1.1.1"

    def test_non_admin_cannot_view_other(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("users:detail", kwargs={"id": other.id}))
        assert response.status_code == 403

    def test_update_self(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            reverse("users:me-update"), {"first_name": "New"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "New"
        assert "ip_address" not in response.data

    def test_update_other_requires_admin(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            reverse("users:update-by-id", kwargs={"id": other.id}),
            {"first_name": "Nope"},
            format="json",
        )
        assert response.status_code == 403

    def test_admin_can_update_other(self, api_client):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=admin)
        response = api_client.patch(
            reverse("users:update-by-id", kwargs={"id": other.id}),
            {"is_blocked": True},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["is_blocked"] is True

    def test_delete_self(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.delete(reverse("users:me-delete"))
        assert response.status_code == 204

    def test_delete_other_requires_admin(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.delete(
            reverse("users:delete-by-id", kwargs={"id": other.id})
        )
        assert response.status_code == 403

    def test_admin_can_delete_other(self, api_client):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        other = User.objects.create_user(email="other@example.com", password="pass1234")
        api_client.force_authenticate(user=admin)
        response = api_client.delete(
            reverse("users:delete-by-id", kwargs={"id": other.id})
        )
        assert response.status_code == 204
        assert not User.objects.filter(id=other.id).exists()

    def test_user_list_admin_only(self, api_client):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("users:list"))
        assert response.status_code == 403

        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )
        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("users:list"))
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert "ip_address" in results[0]
