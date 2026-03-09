# Django Modules
from enum import unique

from django.db.models import (
    Model, CharField, SlugField,
    TextField, ForeignKey, CASCADE, DateTimeField
)

# Project Modules
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser


class Community(Abstract):

    NAME_MAX_LENGTH = 255
    VISIBILITY_MAX_LENGTH = 10
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("secret", "Secret"),
    ]

    name = CharField(
        max_length=NAME_MAX_LENGTH,
    )

    slug = SlugField(
        unique=True,
    )

    description = TextField(
        blank=True
    )

    visibility = CharField(
        max_length=VISIBILITY_MAX_LENGTH,
        choices=VISIBILITY_CHOICES,
    )

    owner = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="owned_communities"
    )

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"


class CommunityMembership(Model):
    ROLE_CHOICES = [
        ("member", "Member"),
        ("moderator", "Moderator"),
        ("organizer", "Organizer"),
    ]
    ROLE_MAX_LENGTH=20
    STATUS_CHOICES = [
        ("active", "Active"),
        ("pending", "Pending"),
        ("banned", "Banned"),
    ]
    STATUS_MAX_LENGTH=20

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )

    community = ForeignKey(
        Community,
        on_delete=CASCADE,
    )

    role = CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
    )

    status = CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
    )

    joined_at = DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ("user", "community")