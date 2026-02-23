# Django Modules
from django.db.models import (
    Model, ForeignKey, CASCADE, FileField, CharField, DateTimeField
)

# Project Modules
from apps.auths.models import CustomUser


class Media(Model):

    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
    ]
    MEDIA_MAX_LENGTH = 10

    owner = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="media"
    )

    file = FileField(
        upload_to="media/%Y/%m/%d/"
    )

    media_type = CharField(
        max_length=MEDIA_MAX_LENGTH,
        choices=MEDIA_TYPE_CHOICES,
    )

    created_at = DateTimeField(
        auto_now_add=True,
    )