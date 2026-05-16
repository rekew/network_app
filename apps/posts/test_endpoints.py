"""Pytest-style tests for posts endpoints.

Function-based tests using `api_client` and `create_user` fixtures.
"""

from typing import Any

import pytest

from django.contrib.auth import get_user_model
from rest_framework import status


pytestmark = pytest.mark.django_db


PREFIXES = [
    "posts",
    "comments",
    "reactions",
    "tags",
    "post-tags",
    "hashtags",
    "post-hashtags",
    "polls",
]


def test_list_authenticated_good(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="post_py", email="pp@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    for prefix in PREFIXES:
        resp = client.get(f"/{prefix}/")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)


def test_list_unauthenticated_bad(client) -> None:
    client.defaults.pop("HTTP_AUTHORIZATION", None)
    for prefix in PREFIXES:
        resp = client.get(f"/{prefix}/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_detail_not_found_bad(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="post_py2", email="pp2@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    for prefix in PREFIXES:
        resp = client.get(f"/{prefix}/999999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
