from rest_framework.serializers import ModelSerializer

from .models import Media


class MediaSerializer(ModelSerializer):
    class Meta:
        model = Media
        fields = (
            "id",
            "owner",
            "file",
            "media_type",
            "created_at",
        )
        read_only_fields = ("id", "owner", "created_at")

