# DJANGO MODULES
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

# THIRD PARTY
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.generics import CreateAPIView

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
    FriendshipSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ReportSerializer,
    UpdateProfileSerializer,
    UpdateUserSerializer,
    UserBlockSerializer,
)


# ---------------------------------------------------
# AUTH
# ---------------------------------------------------

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ---------------------------------------------------
# USER
# ---------------------------------------------------

class UserViewSet(GenericViewSet):

    """
    Viewset for user

    methods: GET, UPDATE, DELETE
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()

    def get_queryset(self) -> QuerySet[CustomUser]:
        return CustomUser.objects.filter(
            id=self.request.user.id,
            deleted_at__isnull=True,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = CustomUserSerializer(self.get_object())
        return Response(serializer.data)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        user = self.get_object()

        serializer = UpdateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        user = self.get_object()

        user.deleted_at = timezone.now()
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------
# PROFILE
# ---------------------------------------------------

class ProfileViewSet(GenericViewSet):

    """
    ViewSet to create user profile

    methods: GET, UPDATE, DELETE
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    queryset = Profile.objects.all()

    def get_queryset(self) -> QuerySet[Profile]:
        return Profile.objects.filter(user=self.request.user)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        serializer = ProfileSerializer(self.get_object())
        return Response(serializer.data)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        profile = self.get_object()

        serializer = UpdateProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        profile = self.get_object()

        profile.deleted_at = timezone.now()
        profile.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------
# FRIENDSHIP
# ---------------------------------------------------

class FriendshipViewSet(ModelViewSet):
    """
    ViewSet to add friends

    methods: GET, POST, UPDATE, DELETE
    """

    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    queryset = Friendship.objects.all()

    def get_queryset(self) -> QuerySet[Friendship]:

        return (
            Friendship.objects.select_related("sender", "receiver")
            .filter(
                models.Q(sender=self.request.user)
                | models.Q(receiver=self.request.user)
            )
            .order_by("-created_at")
        )

    def get_serializer_class(self):

        if self.action == "create":
            return CreateFriendshipSerializer

        if self.action == "destroy":
            return DeleteFriendShipSerializer

        return FriendshipSerializer

    def perform_create(self, serializer):

        receiver_id = self.request.data.get("receiver")

        if receiver_id is None:
            raise ValidationError("receiver is required")

        if receiver_id == self.request.user.id:
            raise ValidationError(
                "You cannot send a friend request to yourself"
            )

        if Friendship.objects.filter(
            models.Q(sender=self.request.user, receiver_id=receiver_id)
            | models.Q(sender_id=receiver_id, receiver=self.request.user),
        ).exists():
            raise ValidationError("Friend request already exists")

        serializer.save(
            sender=self.request.user,
            receiver_id=receiver_id,
        )


# ---------------------------------------------------
# USER BLOCK
# ---------------------------------------------------

class UserBlockViewSet(ModelViewSet):
    """
    ViewSet to block user

    methods: GET, POST, UPDATE, DELETE
    """

    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    queryset = UserBlock.objects.all()

    def get_queryset(self) -> QuerySet[UserBlock]:

        return (
            UserBlock.objects.select_related("blocker", "blocked")
            .filter(blocker=self.request.user)
            .order_by("-blocked_at")
        )

    def get_serializer_class(self):

        if self.action == "create":
            return CreateUserBlockSerializer

        return UserBlockSerializer

    def perform_create(self, serializer):

        blocked_id = self.request.data.get("blocked_id")

        if blocked_id is None:
            raise ValidationError("blocked_id is required")

        if blocked_id == self.request.user.id:
            raise ValidationError("You cannot block yourself")

        if UserBlock.objects.filter(
            blocker=self.request.user,
            blocked_id=blocked_id,
        ).exists():
            raise ValidationError("You have already blocked this user")

        serializer.save(
            blocker=self.request.user,
            blocked_id=blocked_id,
        )


# ---------------------------------------------------
# ACTIVITY LOG
# ---------------------------------------------------

class ActivityLogViewSet(ModelViewSet):

    """
    ViewSet for logging activities

    methods: GET, POST
    """

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    queryset = ActivityLog.objects.all()

    def get_queryset(self) -> QuerySet[ActivityLog]:

        return (
            ActivityLog.objects.filter(
                user=self.request.user,
                deleted_at__isnull=True,
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)


# ---------------------------------------------------
# REPORT
# ---------------------------------------------------

class ReportViewSet(ModelViewSet):
    """
    ViewSet to report 

    methods: GET, POST, UPDATE
    """

    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    queryset = Report.objects.all()

    def get_queryset(self) -> QuerySet[Report]:

        qs = Report.objects.select_related(
            "reporter",
            "handled_by",
        ).order_by("-created_at")

        if self.request.user.is_staff:
            return qs

        return qs.filter(reporter=self.request.user)

    def perform_create(self, serializer):

        serializer.save(reporter=self.request.user)

    def perform_update(self, serializer):

        if not self.request.user.is_staff:
            raise ValidationError(
                "Only staff users can update report status."
            )

        serializer.save(
            handled_by=self.request.user,
        )
