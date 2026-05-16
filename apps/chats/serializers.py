# DRF
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    Serializer,
    ListField,
)

# Project Modules
from .models import Chat, ChatMember, Message


class ChatSerializer(ModelSerializer):
    """Serializers for chat members"""

    class Meta:
        model = Chat
        fields = [
            'id',
            'type',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatMemberSerializer(ModelSerializer):
    """Serializers for Chat Members"""

    username = CharField(source='user.username', read_only=True)

    class Meta:
        model = ChatMember
        fields = [
            'id',
            'chat',
            'user',
            'username',
            'role',
            'joined_at',
        ]
        read_only_fields = ['id', 'joined_at']


class MessageSerializer(ModelSerializer):
    """Serializer class for Messages"""
    class Meta:
        model = Message
        fields = [
            'id',
            'chat',
            'sender',
            'content',
            'is_read',
            'sent_at',
            'reply_to',
        ]
        read_only_fields = ['id', 'sent_at']


class ChatNotFoundSerializer(Serializer):
    """
    Serializer for HTTP 404 Method Not Allowed response.
    """
    detail = CharField()

    class Meta:
        """Customization of the Serializer metadata."""
        fields = (
            "detail",
        )


class ChatResponseSerializer(Serializer):
    """
    Serializer for comment errors.
    """
    type = CharField(
        required=False,
    )

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "type",
        )


class ChatForbiddenSerializer(Serializer):
    """403 — Action not allowed"""
    detail = CharField(default="You do not have permission to perform this action")
 
    class Meta:
        fields = ("detail",)
 

class ChatAlreadyMemberSerializer(Serializer):
    """400 — User is already a member of the chat"""
    detail = CharField(default="User is already a member of this chat")
 
    class Meta:
        fields = ("detail",)
 
 
class ChatNotMemberSerializer(Serializer):
    """404 — User is not a member of the chat"""
    detail = CharField(default="User is not a member of this chat")
 
    class Meta:
        fields = ("detail",)
 