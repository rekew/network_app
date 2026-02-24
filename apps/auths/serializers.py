# DJANGO MODULES
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

# PROJECT MODULES
from apps.auths.models import CustomUser

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


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

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
