# DJANGO MODULES
from django.utils import timezone

# THIRD PARTY MODULES

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# PROJECT MODULES
from .serializers import (
    CustomTokenObtainPairSerializer,
    CustomUserSerializer,
    DeleteUserSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
)
from .models import CustomUser


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return CustomUser.objects.filter(
            id=self.request.user.id,
            deleted_at__isnull=True
        )


class UserUpdateView(UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return CustomUser.objects.filter(
            id=self.request.user.id,
            deleted_at__isnull=True
        )


class UserDeleteView(DestroyAPIView):
    serializer_class = DeleteUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
