# Django Modules
from django.contrib.admin import register

# Unfold Modules
from unfold.admin import ModelAdmin

# Project Modules
from .models import (
    Post, Comment, Reaction,
    Poll, PollOption, PollVote,
    Hashtag, PostHashtag, Tag, PostTag
)


@register(Post)
class PostAdmin(ModelAdmin):
    """
    ModelAdmin for Posts
    """
    list_display = ("id", "author", "community", "pinned", "created_at")
    list_filter = ("pinned", "community")
    search_fields = ("author__email", "author__username", "content")
    date_hierarchy = "created_at"


@register(Comment)
class CommentAdmin(ModelAdmin):
    """
    ModelAdmin for Comments
    """
    list_display = ("id", "post", "author", "parent_comment", "created_at")
    search_fields = ("author__email", "author__username", "content")
    date_hierarchy = "created_at"


@register(Reaction)
class ReactionAdmin(ModelAdmin):
    """
    ModelAdmin for Reactions
    """
    list_display = ("id", "user", "post", "comment", "created_at")
    search_fields = ("author__email", "author__username")
    date_hierarchy = "created_at"


@register(Poll)
class PollAdmin(ModelAdmin):
    """
    ModelAdmin for Polls
    """
    list_display = ("id", "post", "question", "allow_multiple")
    search_fields = ("author__email", "author__username")


@register(Hashtag)
class HashtagAdmin(ModelAdmin):
    """
    ModelAdmin for Hashtags
    """
    list_display = ("id", "name", "created_at")
    search_fields = ("author__email", "author__username")
    date_hierarchy = "created_at"