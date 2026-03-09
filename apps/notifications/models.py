# DJANGO MODULES
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ForeignKey,
    TextField,
    UUIDField,
)

# PROJECT MODULES
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser


class Notification(Abstract):
    """Notification sent from one user to another."""

    CONTENT_MAX_LENGTH = 50

    sender = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="sent_notifications",
    )

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="notifications",
    )

    content = TextField()

    is_read = BooleanField(
        default=False
    )

    content_type = CharField(
        max_length=CONTENT_MAX_LENGTH,
        blank=True,
        null=True,
    )

    object_id = UUIDField(
        blank=True,
        null=True,
    )
