# Django Modules
from django.contrib.admin import register

# Unfold Modules
from unfold.admin import ModelAdmin

# Project Modules
from .models import Chat, Message, ChatMember


@register(Chat)
class ChatAdmin(ModelAdmin):
    """
    Chat Adminka
    """
    list_display = ("id", "type", "created_by")
    list_filter = ("type", )
    search_fields = ("type", )


@register(Message)
class MessageAdmin(ModelAdmin):
    """
    Message Adminka
    """
    list_display = ("id", "chat", "sender", "content", "is_read", "reply_to")
    list_filter = ("chat", )


@register(ChatMember)
class ChatMemberAdmin(ModelAdmin):
    """
    Chat Member Adminka
    """
    list_display = ("id", "chat", "user", "joined_at")
    list_filter = ("chat", )