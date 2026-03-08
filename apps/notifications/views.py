from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


class NotificationCreateView(CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # By default, create notifications for the authenticated user
        serializer.save(user=self.request.user)


class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            if is_read.lower() in ("true", "1"):
                qs = qs.filter(is_read=True)
            elif is_read.lower() in ("false", "0"):
                qs = qs.filter(is_read=False)
        return qs


class NotificationDetailView(RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDeleteView(DestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
