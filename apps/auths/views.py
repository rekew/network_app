# DJANGO MODULES
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

# THIRD PARTY AND PYTHON MODULES
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

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
from .serializers import (
    ActivityLogSerializer,
    CreateFriendshipSerializer,
    CreateUserBlockSerializer,
    CustomTokenObtainPairSerializer,
    CustomUserSerializer,
    DeleteFriendShipSerializer,
    DeleteUserSerializer,
    FriendshipSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ReportSerializer,
    UpdateProfileSerializer,
    UpdateUserSerializer,
    UserBlockSerializer,
)


class RegisterView(CreateAPIView):
    """Endpoint for registering a new user."""

    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT token endpoint using custom validation."""

    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(RetrieveAPIView):
    """Retrieve details of the authenticated user."""

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[CustomUser]:
        """Limit queryset to the current non-deleted user."""
        request: Request = self.request
        return CustomUser.objects.filter(
            id=request.user.id,
            deleted_at__isnull=True,
        )


class UserUpdateView(UpdateAPIView):
    """Update details of the authenticated user."""

    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[CustomUser]:
        """Limit queryset to the current non-deleted user."""
        request: Request = self.request
        return CustomUser.objects.filter(
            id=request.user.id,
            deleted_at__isnull=True,
        )


class UserDeleteView(DestroyAPIView):
    """Soft-delete the authenticated user."""

    serializer_class = DeleteUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[CustomUser]:
        """Limit queryset to the current user."""
        return CustomUser.objects.filter(id=self.request.user.id)

    def destroy(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Soft-delete instead of hard-delete."""
        instance: CustomUser = self.get_object()
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileDetailView(RetrieveAPIView):
    """Retrieve profile details for the authenticated user."""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Profile]:
        """Limit queryset to the current user's non-deleted profile."""
        return Profile.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True,
        )


class ProfileUpdateView(UpdateAPIView):
    """Update the authenticated user's profile."""

    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Profile]:
        """Limit queryset to the current user's profile."""
        return Profile.objects.filter(user=self.request.user)


class ProfileDeleteView(DestroyAPIView):
    """Soft-delete the authenticated user's profile."""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Profile]:
        """Limit queryset to the current user's non-deleted profile."""
        return Profile.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True,
        )

    def destroy(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Soft-delete the profile."""
        instance: Profile = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendshipCreateView(CreateAPIView):
    """Create a friendship request from the authenticated user."""

    serializer_class = CreateFriendshipSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: CreateFriendshipSerializer) -> None:
        """Validate and persist a new friendship request."""
        request: Request = self.request
        receiver_id: Any = request.data.get("receiver")
        if receiver_id is None:
            raise ValidationError("receiver is required")
        if receiver_id == request.user.id:
            raise ValidationError(
                "You cannot send a friend request to yourself",
            )
        if Friendship.objects.filter(
            models.Q(sender=request.user, receiver_id=receiver_id)
            | models.Q(sender_id=receiver_id, receiver=request.user),
        ).exists():
            raise ValidationError("Friend request already exists")
        serializer.save(sender=request.user, receiver_id=receiver_id)


class FriendshipListView(ListAPIView):
    """List all friendship relations for the authenticated user."""

    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Friendship]:
        """Return friendships where the user is sender or receiver."""
        request: Request = self.request
        return (
            Friendship.objects.select_related("sender", "receiver")
            .filter(
                models.Q(sender=request.user)
                | models.Q(receiver=request.user),
            )
            .order_by("-created_at")
        )


class FriendshipDeleteView(DestroyAPIView):
    """Delete a friendship relation."""

    serializer_class = DeleteFriendShipSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Friendship]:
        """Limit queryset to friendships involving the current user."""
        request: Request = self.request
        return Friendship.objects.filter(
            models.Q(sender=request.user) | models.Q(receiver=request.user),
        )


class UserBlockCreateView(CreateAPIView):
    """Create a user block from the authenticated user."""

    serializer_class = CreateUserBlockSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: CreateUserBlockSerializer) -> None:
        """Validate and persist a new user block."""
        request: Request = self.request
        blocked_id: Any = request.data.get("blocked_id")
        if blocked_id is None:
            raise ValidationError("blocked_id is required")
        if blocked_id == request.user.id:
            raise ValidationError("You cannot block yourself")

        if UserBlock.objects.filter(
            blocker=request.user,
            blocked_id=blocked_id,
        ).exists():
            raise ValidationError("You have already blocked this user")

        serializer.save(blocker=request.user, blocked_id=blocked_id)


class UserBlockListView(ListAPIView):
    """List all blocks created by the authenticated user."""

    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[UserBlock]:
        """Return blocks where the user is the blocker."""
        request: Request = self.request
        return (
            UserBlock.objects.select_related("blocker", "blocked")
            .filter(blocker=request.user)
            .order_by("-blocked_at")
        )


class UserBlockDeleteView(DestroyAPIView):
    """Delete an existing user block."""

    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[UserBlock]:
        """Limit queryset to blocks created by the current user."""
        return UserBlock.objects.filter(blocker=self.request.user)


class ActivityLogCreateView(CreateAPIView):
    """Create a new activity log entry for the user."""

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: ActivityLogSerializer) -> None:
        """Attach the current user to the log entry."""
        serializer.save(user=self.request.user)


class ActivityLogListView(ListAPIView):
    """List activity log entries for the authenticated user."""

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[ActivityLog]:
        """Return non-deleted logs for the current user."""
        request: Request = self.request
        return (
            ActivityLog.objects.filter(
                user=request.user,
                deleted_at__isnull=True,
            )
            .order_by("-created_at")
        )


class ReportCreateView(CreateAPIView):
    """Create a new report entry."""

    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: ReportSerializer) -> None:
        """Attach the reporting user to the report."""
        serializer.save(reporter=self.request.user)


class ReportListView(ListAPIView):
    """List report entries; staff see all, others only their own."""

    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Report]:
        """Return relevant reports depending on user role."""
        request: Request = self.request
        base_qs: QuerySet[Report] = Report.objects.select_related(
            "reporter",
            "handled_by",
        ).order_by("-created_at")
        if request.user.is_staff:
            return base_qs
        return base_qs.filter(reporter=request.user)


class ReportDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single report."""

    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Report]:
        """Return reports visible to the current user."""
        request: Request = self.request
        qs: QuerySet[Report] = Report.objects.select_related(
            "reporter",
            "handled_by",
        )
        if request.user.is_staff:
            return qs
        return qs.filter(reporter=request.user)

    def perform_update(self, serializer: ReportSerializer) -> None:
        """Allow only staff to update the report status."""
        request: Request = self.request
        if not request.user.is_staff:
            raise ValidationError("Only staff users can update report status.")
        serializer.save(handled_by=request.user)
