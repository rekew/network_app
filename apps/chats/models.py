# Django Modules
from django.db.models import (
    Model, CharField, ForeignKey,
    CASCADE, TextField, BooleanField,
    DateTimeField, SET_NULL, TextChoices
)
from django.utils.translation import gettext_lazy as _

# Project Modules
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser


class Chat(Abstract):

    TYPE_MAX_LENGTH = 10

    class ChatType(TextChoices):
        PRIVATE = "private", _("Private")
        GROUP = "group", _("Group")

    type = CharField(
        max_length=TYPE_MAX_LENGTH,
        choices=TextChoices,
    )
    created_by = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )


class Message(Model):

    chat = ForeignKey(
        Chat,
        on_delete=CASCADE,
        related_name="messages",
    )

    sender = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )

    content = TextField()

    is_read = BooleanField(
        default=False,
    )

    sent_at = DateTimeField(
        auto_now_add=True
    )

    reply_to = ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )


class ChatMember(Model):

    class RoleType(TextChoices):
        MEMBER = "member", _("Member")
        ADMIN = "admin", _("Admin")

    ROLE_MAX_LENGTH = 10

    chat = ForeignKey(
        Chat,
        on_delete=CASCADE,
        related_name="members"
    )

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="chat_memberships"
    )

    role = CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=RoleType,
        default='member'
    )

    joined_at = DateTimeField(
        auto_now_add=True
    )
