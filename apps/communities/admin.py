# Django Modules
from django.contrib.admin import register

# Project Modules
from .models import Community, CommunityMembership

# Unfold Modules
from unfold.admin import ModelAdmin

@register(Community)
class CommunityAdmin(ModelAdmin):
    """
    ModelAdmin for Posts
    """
    list_display = ("id", "name","owner", "description", "visibility", "created_at")
    list_filter = ("visibility", "owner")
    search_fields = ("name", )
    date_hierarchy = "created_at"

@register(CommunityMembership)
class CommunityMembershipAdmin(ModelAdmin):
    """
    ModelAdmin for Posts
    """
    list_display = ("id", "user","community", "role", "status", "joined_at")
    list_filter = ("community", )
    search_fields = ("user", )
    date_hierarchy = "joined_at"