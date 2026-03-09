# DJANGO MODULES
from django.db.models import QuerySet

# THIRD PARTY AND PYTHON MODULES
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from typing import Any

# PROJECT MODULES
from .models import Notification
from .serializers import NotificationSerializer


class NotificationCreateView(CreateAPIView):
    """Create notifications from a sender to a recipient."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: NotificationSerializer) -> None:
        """Attach sender/recipient to the new notification."""
        request: Request = self.request
        recipient_id: Any = request.data.get("user_id")
        if recipient_id is None:
            raise ValidationError("user_id (recipient) is required")
        if str(recipient_id) == str(request.user.id):
            raise ValidationError("You cannot send a notification to yourself")

        serializer.save(sender=request.user, user_id=recipient_id)


class NotificationListView(ListAPIView):
    """List notifications for the authenticated recipient."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Notification]:
        """Return notifications for the current user, optionally filtered."""
        request: Request = self.request
        qs: QuerySet[Notification] = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        is_read_param: str | None = request.query_params.get("is_read")
        if is_read_param is not None:
            lowered = is_read_param.lower()
            if lowered in ("true", "1"):
                qs = qs.filter(is_read=True)
            elif lowered in ("false", "0"):
                qs = qs.filter(is_read=False)
        return qs


class NotificationDetailView(RetrieveUpdateAPIView):
    """Retrieve or update a single notification for the recipient."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Notification]:
        """Limit queryset to notifications belonging to the current user."""
        return Notification.objects.filter(user=self.request.user)


class NotificationDeleteView(DestroyAPIView):
    """Delete a notification for the authenticated recipient."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Notification]:
        """Limit queryset to notifications belonging to the current user."""
        return Notification.objects.filter(user=self.request.user)
