"""Pytest configuration for the prayer-wall project."""

import pytest


@pytest.fixture
def api_client():
    """Return a DRF API client instance."""
    from rest_framework.test import APIClient

    return APIClient()
