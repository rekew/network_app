# DJANGO MODULES
from django.utils import timezone
from django.db import models

# THIRD PARTY MODULES

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    ValidationError,
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
    ProfileSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UpdateUserSerializer,
    FriendshipSerializer,
)
from .models import CustomUser, Friendship, Profile


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


class ProfileCreateView(CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileDetailView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Profile.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )


class ProfileUpdateView(UpdateAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Profile.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileDeleteView(DestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Profile.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FriendshipCreateView(CreateAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver_id")
        if receiver_id is None:
            raise ValidationError("receiver_id is required")
        if receiver_id == self.request.user.id:
            raise ValidationError("You cannot send a friend request to yourself")
        serializer.save(sender=self.request.user, receiver_id=receiver_id)

class FriendshipListView(ListAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Friendship.objects.filter(
            models.Q(sender=self.request.user) | models.Q(receiver=self.request.user),
            deleted_at__isnull=True
        )

class FriendshipDeleteView(DestroyAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Friendship.objects.filter(
            models.Q(sender=self.request.user) | models.Q(receiver=self.request.user)
        )