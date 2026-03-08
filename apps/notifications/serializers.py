from rest_framework.serializers import ModelSerializer

from .models import Notification


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "user",
            "content",
            "is_read",
            "content_type",
            "object_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

