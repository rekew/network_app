# Django Modules
from django.db.models import (
    Model, CharField, SlugField,
    TextField, ForeignKey, CASCADE, DateTimeField,
    TextChoices
)

# Project Modules
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser


class Community(Abstract):

    NAME_MAX_LENGTH = 255
    VISIBILITY_MAX_LENGTH = 10
    class VisibilityType(TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        SECRET = "secret", "Secret"
    

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
        MEMBER = "member", "Member"
        MODERATOR = "moderator", "Moderator"
        ORANIZER = "organizer", "Organizer"
    
    class StatusType(TextChoices):
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending"
        BANNED = "banned", "Banned"
    
    STATUS_MAX_LENGTH=20
    ROLE_MAX_LENGTH=20
    
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