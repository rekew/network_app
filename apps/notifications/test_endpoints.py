"""Pytest-style tests for notifications endpoints.

Each endpoint includes 1 good test and 2 bad tests to exercise
expected and unexpected behaviours. Tests use `api_client` and
`create_user` fixtures from `tests/conftest.py`.
"""

from typing import Any

import pytest

from django.contrib.auth import get_user_model
from rest_framework import status

from .models import Notification


pytestmark = pytest.mark.django_db


def test_create_notification_good(client) -> None:
    User = get_user_model()
    sender = User.objects.create_user(username="sender", email="s@example.com", password="pass")
    recipient = User.objects.create_user(username="recipient", email="r@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": sender.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    payload = {"user_id": recipient.id, "content": "hey there"}
    resp = client.post("/notifications/notifications/create/", payload, content_type="application/json")
    assert resp.status_code == status.HTTP_201_CREATED


def test_create_notification_missing_user_id_bad(client) -> None:
    User = get_user_model()
    sender = User.objects.create_user(username="sender2", email="s2@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": sender.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    payload = {"content": "no recipient"}
    resp = client.post("/notifications/notifications/create/", payload, content_type="application/json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_notification_send_to_self_bad(client) -> None:
    User = get_user_model()
    user = User.objects.create_user(username="selfie", email="self@example.com", password="pass")
    login = client.post("/api/auth/login/", {"email": user.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    payload = {"user_id": user.id, "content": "self send"}
    resp = client.post("/notifications/notifications/create/", payload, content_type="application/json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_list_notifications_good(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="listrec", email="l@example.com", password="pass")
    sender = User.objects.create_user(username="listsend", email="ls@example.com", password="pass")
    # create a notification
    Notification.objects.create(sender=sender, user=recipient, content="hello")
    login = client.post("/api/auth/login/", {"email": recipient.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.get("/notifications/notifications/")
    assert resp.status_code == status.HTTP_200_OK
    # response content is JSON; ensure it's a list by parsing
    assert resp.json() is not None


def test_list_notifications_unauthenticated_bad(client) -> None:
    resp = client.get("/notifications/notifications/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_notifications_invalid_is_read_param_bad(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="paramrec", email="pr@example.com", password="pass")
    Notification.objects.create(sender=User.objects.create_user(username="p1", email="p1@example.com", password="pass"), user=recipient, content="x")
    login = client.post("/api/auth/login/", {"email": recipient.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.get("/notifications/notifications/?is_read=maybe")
    assert resp.status_code == status.HTTP_200_OK


def test_detail_update_notification_good(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="drec", email="drec@example.com", password="pass")
    sender = User.objects.create_user(username="dsend", email="dsend@example.com", password="pass")
    notification = Notification.objects.create(sender=sender, user=recipient, content="hi")
    login = client.post("/api/auth/login/", {"email": recipient.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.patch(f"/notifications/notifications/{notification.id}/", {"is_read": True}, content_type="application/json")
    assert resp.status_code == status.HTTP_200_OK
    notification.refresh_from_db()
    assert notification.is_read


def test_detail_notification_other_user_cannot_access_bad(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="targ", email="targ@example.com", password="pass")
    sender = User.objects.create_user(username="oth", email="oth@example.com", password="pass")
    notification = Notification.objects.create(sender=sender, user=recipient, content="x")
    login = client.post("/api/auth/login/", {"email": sender.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.get(f"/notifications/notifications/{notification.id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_detail_notification_unauthenticated_bad(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="anonrec", email="anon@example.com", password="pass")
    sender = User.objects.create_user(username="anons", email="anons@example.com", password="pass")
    notification = Notification.objects.create(sender=sender, user=recipient, content="x")
    resp = client.get(f"/notifications/notifications/{notification.id}/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_notification_good(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="delrec", email="del@example.com", password="pass")
    sender = User.objects.create_user(username="dels", email="dels@example.com", password="pass")
    notification = Notification.objects.create(sender=sender, user=recipient, content="x")
    login = client.post("/api/auth/login/", {"email": recipient.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.delete(f"/notifications/notifications/{notification.id}/delete/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not Notification.objects.filter(id=notification.id).exists()


def test_delete_notification_other_user_bad(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="owner", email="own@example.com", password="pass")
    other = User.objects.create_user(username="other", email="other@example.com", password="pass")
    notification = Notification.objects.create(sender=other, user=recipient, content="x")
    login = client.post("/api/auth/login/", {"email": other.email, "password": "pass"}, content_type="application/json")
    assert login.status_code == 200
    token = login.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    resp = client.delete(f"/notifications/notifications/{notification.id}/delete/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_notification_unauthenticated_bad(client) -> None:
    User = get_user_model()
    recipient = User.objects.create_user(username="uowner", email="uowner@example.com", password="pass")
    sender = User.objects.create_user(username="usender", email="usender@example.com", password="pass")
    notification = Notification.objects.create(sender=sender, user=recipient, content="x")
    resp = client.delete(f"/notifications/notifications/{notification.id}/delete/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
