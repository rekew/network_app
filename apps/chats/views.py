# Django Modules
from django.db import transaction
from django.db.models import QuerySet

# Django Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response as DRFResponse
from rest_framework.request import Request as DRFRequest
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_204_NO_CONTENT,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

# Python Modules
from typing import Any

# Project Modules
from .models import Chat, ChatMember, Message
from apps.auths.models import CustomUser
from .serializers import (
    ChatSerializer,
    ChatMemberSerializer,
    MessageSerializer,
)


class ChatViewSet(ViewSet):
    """ViewSet for Chats"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return (
            Chat.objects.filter(members__user=self.request.user)
            .select_related("created_by")
            .prefetch_related("members__user")
            .distinct()
        )

    def list(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        queryset = self.get_queryset()
        serializer = ChatSerializer(queryset, many=True)
        return DRFResponse(data=serializer.data, status=HTTP_200_OK)

    def create(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        chat_type = request.data.get("type")
        opponent_id = request.data.get("opponent_id")

        if chat_type == "private":
            if not opponent_id:
                return DRFResponse(
                    {"detail": "opponent_id is required"},
                    status=HTTP_400_BAD_REQUEST,
                )

            if str(opponent_id) == str(request.user.id):
                return DRFResponse(
                    {"detail": "Cannot start a chat with yourself"},
                    status=HTTP_400_BAD_REQUEST,
                )

            if not CustomUser.objects.filter(id=opponent_id).exists():
                return DRFResponse(
                    {"detail": "User not found"},
                    status=HTTP_404_NOT_FOUND,
                )

            existing_chat = (
                Chat.objects.filter(type="private", members__user=request.user)
                .filter(members__user_id=opponent_id)
                .distinct()
                .first()
            )
            if existing_chat:
                return DRFResponse(
                    ChatSerializer(existing_chat).data,
                    status=HTTP_200_OK,
                )

        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            chat = serializer.save(created_by=request.user)
            ChatMember.objects.create(chat=chat, user=request.user, role="admin")

            if chat_type == "private":
                ChatMember.objects.create(
                    chat=chat, user_id=opponent_id, role="member"
                )

            elif chat_type == "group":
                member_ids = request.data.get("members", [])
                if member_ids:
                    unique_ids = set(int(m) for m in member_ids) - {request.user.id}
                    ChatMember.objects.bulk_create([
                        ChatMember(chat=chat, user_id=m_id, role="member")
                        for m_id in unique_ids
                    ])

        return DRFResponse(ChatSerializer(chat).data, status=HTTP_201_CREATED)

    def retrieve(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        try:
            chat = self.get_queryset().get(id=kwargs["pk"])
        except Chat.DoesNotExist:
            return DRFResponse(
                {"detail": "Chat does not exist"},
                status=HTTP_404_NOT_FOUND,
            )
        serializer = ChatSerializer(chat)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def destroy(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        """Destroy the chat"""
        try:
            chat = self.get_queryset().get(id=kwargs["pk"])
        except Chat.DoesNotExist:
            return DRFResponse(
                {"detail": "Chat does not exist"},
                status=HTTP_404_NOT_FOUND,
            )

        membership = ChatMember.objects.filter(
            user=request.user, chat=chat
        ).first()
        if not membership or membership.role != "admin":
            return DRFResponse(
                {"detail": "Only admins can delete this chat"},
                status=HTTP_403_FORBIDDEN,
            )

        chat.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add_member",
        permission_classes=[IsAuthenticated],
    )
    def add_member(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        try:
            chat = self.get_queryset().get(id=kwargs["pk"])
        except Chat.DoesNotExist:
            return DRFResponse(
                {"detail": "Chat does not exist"},
                status=HTTP_404_NOT_FOUND,
            )

        if chat.type == "private":
            return DRFResponse(
                {"detail": "Cannot add members to a private chat"},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            membership = ChatMember.objects.get(user=request.user, chat=chat)
            if membership.role != "admin":
                return DRFResponse(
                    {"detail": "Only admins can add members to the group"},
                    status=HTTP_403_FORBIDDEN,
                )
        except ChatMember.DoesNotExist:
            return DRFResponse(
                {"detail": "You are not a member of this chat"},
                status=HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user")
        if not user_id:
            return DRFResponse(
                {"detail": "user field is required"},
                status=HTTP_400_BAD_REQUEST,
            )

        if ChatMember.objects.filter(user_id=user_id, chat=chat).exists():
            return DRFResponse(
                {"detail": "User is already a member of this chat"},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = ChatMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chat=chat)
            return DRFResponse(data=serializer.data, status=HTTP_201_CREATED)

        return DRFResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(
        methods=["DELETE"],
        detail=True,
        url_path="remove_member",
        permission_classes=[IsAuthenticated],
    )
    def remove_member(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        try:
            chat = self.get_queryset().get(id=kwargs["pk"])
        except Chat.DoesNotExist:
            return DRFResponse(
                {"detail": "Chat does not exist"},
                status=HTTP_404_NOT_FOUND,
            )

        requester = ChatMember.objects.filter(
            user=request.user, chat=chat
        ).first()
        if not requester or requester.role != "admin":
            return DRFResponse(
                {"detail": "Only admins can remove members"},
                status=HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user")
        try:
            member = ChatMember.objects.get(user_id=user_id, chat=chat)
        except ChatMember.DoesNotExist:
            return DRFResponse(
                {"detail": "User is not a member of this chat"},
                status=HTTP_404_NOT_FOUND,
            )

        member.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=True,
        url_path="members",
        permission_classes=[IsAuthenticated],
    )
    def members(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        """Get all members of the chat"""
        try:
            chat = self.get_queryset().get(id=kwargs["pk"])
        except Chat.DoesNotExist:
            return DRFResponse(
                {"detail": "Chat does not exist"},
                status=HTTP_404_NOT_FOUND,
            )

        memberships: QuerySet[ChatMember] = (
            ChatMember.objects.filter(chat=chat)
            .select_related("user")
            .order_by("joined_at")
        )
        serializer = ChatMemberSerializer(memberships, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="send_message",
        permission_classes=[IsAuthenticated],
    )
    def send_message(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any,
    ) -> DRFResponse:
        """Send a message to the chat"""
        try:
            chat = self.get_queryset().get(id=kwargs["pk"])
        except Chat.DoesNotExist:
            return DRFResponse(
                {"detail": "Chat does not exist"},
                status=HTTP_404_NOT_FOUND,
            )

        if not ChatMember.objects.filter(user=request.user, chat=chat).exists():
            return DRFResponse(
                {"detail": "You are not a member of this chat"},
                status=HTTP_403_FORBIDDEN,
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chat=chat, sender=request.user)
            return DRFResponse(serializer.data, status=HTTP_201_CREATED)

        return DRFResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)