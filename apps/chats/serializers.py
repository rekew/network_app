# DRF
from rest_framework.serializers import ModelSerializer, CharField

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
