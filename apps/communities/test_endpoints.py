"""Pytest-style tests for communities endpoints."""

from typing import Any

import pytest

from django.contrib.auth import get_user_model
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_list_good(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="comm_py", email="cp@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.get("/communities/")
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)


def test_list_unauthenticated_bad(client) -> None:
    client.defaults.pop("HTTP_AUTHORIZATION", None)
    resp = client.get("/communities/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_detail_not_found_bad(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="comm_py2", email="cp2@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.get("/communities/999999/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
