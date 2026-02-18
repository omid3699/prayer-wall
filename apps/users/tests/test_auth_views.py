import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAuthTokenEndpoint:
    def test_obtain_token_with_email_credentials(self, api_client):
        password = "pass1234"
        user = User.objects.create_user(email="user@example.com", password=password)

        response = api_client.post(
            reverse("users:api-token-auth"),
            {"email": user.email, "password": password},
            format="json",
        )

        assert response.status_code == 200
        assert "token" in response.data
        assert response.data["token"]

    def test_invalid_credentials_return_error(self, api_client):
        response = api_client.post(
            reverse("users:api-token-auth"),
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )

        assert response.status_code == 400
        assert (
            "Unable to log in with provided credentials."
            in response.data["non_field_errors"][0]
        )

    def test_missing_fields_returns_error(self, api_client):
        response = api_client.post(reverse("users:api-token-auth"), {}, format="json")

        assert response.status_code == 400
        assert "email" in response.data
        assert "password" in response.data
