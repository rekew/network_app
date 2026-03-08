from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Media
from .serializers import MediaSerializer


class MediaCreateView(CreateAPIView):
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MediaListView(ListAPIView):
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Media.objects.filter(owner=self.request.user).order_by("-created_at")


class MediaDetailView(RetrieveUpdateAPIView):
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "id"

    def get_queryset(self):
        return Media.objects.filter(owner=self.request.user)


class MediaDeleteView(DestroyAPIView):
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Media.objects.filter(owner=self.request.user)
