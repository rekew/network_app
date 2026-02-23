# Django Modules
from django.db.models import (
    ForeignKey, CASCADE, TextField,
    BooleanField, CharField, UUIDField
)

# Project Modules
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser


class Notification(Abstract):

    CONTENT_MAX_LENGTH=50

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="notifications"
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