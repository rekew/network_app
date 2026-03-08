# DJANGO MODULES
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

# PROJECT MODULES
from .models import CustomUser, Profile, Friendship

# THIRD PARTY MODULES
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomUserSerializer(ModelSerializer):
    """
    Serializer for CustomUser model
    """

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
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
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
    class Meta:
        model = Profile
        fields = ("id", "display_name", "bio", "interests", "is_verified")
        extra_kwargs = {
            "id":          {"read_only": True},
            "is_verified": {"read_only": True},
        }


class UpdateProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "display_name", "bio", "interests")
        extra_kwargs = {
            "id":           {"read_only": True},
            "display_name": {"required": False},
            "bio":          {"required": False},
            "interests":    {"required": False},
        }


class FriendshipSerializer(ModelSerializer):
    class Meta:
        model = Friendship
        fields = ("id", "sender", "receiver", "status", "created_at")
        read_only_fields = ("id", "sender", "status", "created_at")


class DeleteFriendShipSerializer(ModelSerializer):
    class Meta:
        model = Friendship
        read_only_fields = ("id",)
