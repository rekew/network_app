# Django Modules
from django.db.models import (
    Model, CharField, SlugField,
    TextField, ForeignKey, CASCADE, DateTimeField,
    TextChoices
)
from django.utils.translation import gettext_lazy as _

# Project Modules
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser


class Community(Abstract):

    NAME_MAX_LENGTH = 255
    VISIBILITY_MAX_LENGTH = 10

    class VisibilityType(TextChoices):
        PUBLIC = "public", _("Public")
        PRIVATE = "private", _("Private")
        SECRET = "secret", _("Secret")

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
        choices=VisibilityType,
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
    class RoleType(TextChoices):
        MEMBER = "member", _("Member")
        MODERATOR = "moderator", _("Moderator")
        ORANIZER = "organizer", _("Organizer")

    class StatusType(TextChoices):
        ACTIVE = "active", _("Active")
        PENDING = "pending", _("Pending")
        BANNED = "banned", _("Banned")

    STATUS_MAX_LENGTH = 20
    ROLE_MAX_LENGTH = 20

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )

    community = ForeignKey(
        Community,
        on_delete=CASCADE,
        related_name='memberships'
    )

    role = CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=RoleType,
    )

    status = CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=StatusType,
    )

    joined_at = DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ("user", "community")
