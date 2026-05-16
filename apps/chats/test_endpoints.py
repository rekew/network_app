"""Pytest-style tests for chats endpoints.

These tests assume the chats viewset is mounted at `/chats/` via a router.
"""

from typing import Any

import pytest

from django.contrib.auth import get_user_model
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_list_good(client) -> None:
    User = get_user_model()
    user1 = User.objects.create_user(username="c1", email="c1@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user1.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.get("/chats/")
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)


def test_list_unauthenticated_bad(client) -> None:
    client.defaults.pop("HTTP_AUTHORIZATION", None)
    resp = client.get("/chats/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_private_missing_opponent_bad(client) -> None:
    User = get_user_model()
    user1 = User.objects.create_user(username="c2", email="c2@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user1.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    payload = {"type": "private"}
    resp = client.post("/chats/", payload, content_type="application/json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
