# DJANGO MODULES
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

# THIRD PARTY AND PYTHON MODULES
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from typing import Any

# PROJECT MODULES
from .models import (
    ActivityLog,
    CustomUser,
    Friendship,
    Profile,
    Report,
    UserBlock,
)


class CustomUserSerializer(ModelSerializer):
    """Serializer for the CustomUser model."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class UpdateUserSerializer(ModelSerializer):
    """Serializer used for updating user data."""
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password",)
        extra_kwargs = {
            "id": {"read_only": True},
            "username": {"required": False},
            "email": {"required": False},
            "password": {"required": False},
        }


class DeleteUserSerializer(ModelSerializer):
    """Serializer used for soft-deleting a user."""
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password",)
        extra_kwargs = {
            "id": {"write_only": True},
            "username": {"write_only": True},
            "email": {"write_only": True},
            "password": {"write_only": True},
        }


class RegisterSerializer(ModelSerializer):
    """Serializer used for user registration."""
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")

    def create(self, validated_data: dict[str, Any]) -> CustomUser:
        """Create a user and its associated profile."""
        user = CustomUser.objects.create_user(**validated_data)
        Profile.objects.create(user=user, display_name=user.username)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer validating using email as username."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        user = authenticate(
            username=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise ValidationError("Invalid credentials")

        update_last_login(None, user)
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class ProfileSerializer(ModelSerializer):
    """Read/write serializer for profile data."""
    class Meta:
        model = Profile
        fields = (
            "id",
            "display_name",
            "bio",
            "interests",
            "is_verified",
            "media_file",
        )
        extra_kwargs = {
            "id":          {"read_only": True},
            "is_verified": {"read_only": True},
        }


class UpdateProfileSerializer(ModelSerializer):
    """Serializer used for partial profile updates."""

    class Meta:
        model = Profile
        fields = ("id", "display_name", "bio", "interests", "media_file")
        extra_kwargs = {
            "id":           {"read_only": True},
            "display_name": {"required": False},
            "bio":          {"required": False},
            "interests":    {"required": False},
            "media_file":   {"required": False},
        }


class FriendshipSerializer(ModelSerializer):
    """Serializer for reading friendship relationships."""
    class Meta:
        model = Friendship
        fields = ("id", "sender", "receiver", "status", "created_at")
        read_only_fields = ("id", "sender", "status", "created_at")


class CreateFriendshipSerializer(ModelSerializer):
    """Serializer used when creating a friendship."""
    class Meta:
        model = Friendship
        fields = '__all__'
        read_only_fields = ("id", "sender", "status", "created_at")


class DeleteFriendShipSerializer(ModelSerializer):
    """Serializer used when deleting a friendship."""
    class Meta:
        model = Friendship
        read_only_fields = ("id",)


class UserBlockSerializer(ModelSerializer):
    """Serializer for reading user block relationships."""
    class Meta:
        model = UserBlock
        fields = ("id", "blocker", "blocked", "reason", "blocked_at")
        read_only_fields = ("id", "blocker", "blocked_at")


class CreateUserBlockSerializer(ModelSerializer):
    """Serializer used when creating a user block."""
    class Meta:
        model = UserBlock
        fields = ("blocked_id", "reason")
        read_only_fields = ("id", "blocker", "blocked_at")


class ActivityLogSerializer(ModelSerializer):
    """Serializer for activity log entries."""
    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "user",
            "details",
            "user_agent",
            "action_type",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")


class ReportSerializer(ModelSerializer):
    """Serializer for user-submitted reports."""
    class Meta:
        model = Report
        fields = (
            "id",
            "reporter",
            "content_type",
            "object_type",
            "reason",
            "status",
            "handled_by",
            "created_at",
        )
        read_only_fields = (
            "id",
            "reporter",
            "status",
            "handled_by",
            "created_at",
        )
