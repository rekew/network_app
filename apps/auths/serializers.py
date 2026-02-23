# DRF modules
from rest_framework.serializers import ModelSerializer
# Project modules
from apps.auths.models import CustomUser


class CustomUserSerializer(ModelSerializer):
    """
    Serializer for CustomUser model
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username"
            "created_at",
            "updated_at",
        ]