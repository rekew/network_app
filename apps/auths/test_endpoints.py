"""Pytest-style tests for auths endpoints.

Includes authenticated list checks and negative tests for unauthenticated
access and missing detail records. Uses `api_client` and `create_user`
fixtures from `tests/conftest.py`.
"""

from typing import Any

import pytest

from django.contrib.auth import get_user_model
from rest_framework import status


pytestmark = pytest.mark.django_db


PREFIXES = [
    "users",
    "profiles",
    "friendships",
    "user-blocks",
    "activity-logs",
    "reports",
]


def test_list_authenticated_good(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="pytest_user", email="p@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    for prefix in PREFIXES:
        resp = client.get(f"/api/{prefix}/")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)


def test_list_unauthenticated_bad(client) -> None:
    # ensure no auth header
    client.defaults.pop("HTTP_AUTHORIZATION", None)
    for prefix in PREFIXES:
        resp = client.get(f"/api/{prefix}/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_detail_not_found_bad(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="pytest_user2", email="p2@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    for prefix in PREFIXES:
        resp = client.get(f"/api/{prefix}/999999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
