# DJANGO MODULES
from django.utils import timezone
from django.db import models

# THIRD PARTY MODULES

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

# PROJECT MODULES
from .serializers import (
    ActivityLogSerializer,
    CustomTokenObtainPairSerializer,
    CustomUserSerializer,
    DeleteUserSerializer,
    DeleteFriendShipSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ReportSerializer,
    UpdateProfileSerializer,
    UpdateUserSerializer,
    FriendshipSerializer,
    UserBlockSerializer,
)
from .models import ActivityLog, CustomUser, Friendship, Profile, Report, UserBlock


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
        return (
            Friendship.objects.select_related("sender", "receiver")
            .filter(
                models.Q(sender=self.request.user)
                | models.Q(receiver=self.request.user),
                deleted_at__isnull=True,
            )
            .order_by("-created_at")
        )


class FriendshipDeleteView(DestroyAPIView):
    serializer_class = DeleteFriendShipSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Friendship.objects.filter(
            models.Q(sender=self.request.user) | models.Q(receiver=self.request.user)
        )


class UserBlockCreateView(CreateAPIView):
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        blocked_id = self.request.data.get("blocked_id")
        if blocked_id is None:
            raise ValidationError("blocked_id is required")
        if blocked_id == self.request.user.id:
            raise ValidationError("You cannot block yourself")

        if UserBlock.objects.filter(
            blocker=self.request.user, blocked_id=blocked_id
        ).exists():
            raise ValidationError("You have already blocked this user")

        serializer.save(blocker=self.request.user, blocked_id=blocked_id)


class UserBlockListView(ListAPIView):
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            UserBlock.objects.select_related("blocker", "blocked")
            .filter(blocker=self.request.user)
            .order_by("-blocked_at")
        )


class UserBlockDeleteView(DestroyAPIView):
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return UserBlock.objects.filter(blocker=self.request.user)


class ActivityLogCreateView(CreateAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityLogListView(ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ActivityLog.objects.filter(
                user=self.request.user, deleted_at__isnull=True
            )
            .order_by("-created_at")
        )


class ReportCreateView(CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class ReportListView(ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_qs = Report.objects.select_related("reporter", "handled_by").order_by(
            "-created_at"
        )
        if self.request.user.is_staff:
            return base_qs
        return base_qs.filter(reporter=self.request.user)


class ReportDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        qs = Report.objects.select_related("reporter", "handled_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(reporter=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise ValidationError("Only staff users can update report status.")
        serializer.save(handled_by=self.request.user)