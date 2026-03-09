# THIRD PARTY AND PYTHON MODULES
from rest_framework.serializers import ModelSerializer

# PROJECT MODULES
from .models import Notification


class NotificationSerializer(ModelSerializer):
    """Serializer for the Notification model."""

    class Meta:
        model = Notification
        fields = (
            "id",
            "sender",
            "user",
            "content",
            "is_read",
            "content_type",
            "object_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "sender", "user", "created_at", "updated_at")
