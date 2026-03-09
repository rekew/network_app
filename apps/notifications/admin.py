# Django Modules
from django.contrib.admin import register

# Unfold Modules
from unfold.admin import ModelAdmin

# Project Modules
from .models import Notification

@register(Notification)
class NotificationAdmin(ModelAdmin):
    """
        Notification Admin
    """
    list_display = ("id", "sender", "user", "content", "is_read", "object_id")
    list_filter = ("sender", "content_type")
    date_hierarchy = "created_at"