"""Project-level pytest fixtures.

Placing `conftest.py` at the repository root ensures fixtures are
available to tests located under `apps/`.
"""

from typing import Any, Callable

import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF APIClient instance for making requests."""
    return APIClient()


@pytest.fixture
def create_user() -> Callable[..., Any]:
    """Simple factory to create users in tests."""

    def _factory(**kwargs: Any):
        User = get_user_model()
        defaults = {"username": "testuser", "email": "t@example.com", "password": "pass"}
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _factory
