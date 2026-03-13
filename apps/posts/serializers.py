# DRF modules
from attr import fields
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)
from drf_spectacular.utils import extend_schema_field
# Project modules
from apps.posts.models import (
    Post, Comment, Reaction,
    Poll, PollOption, PollVote,
    Hashtag, PostHashtag,
    Tag, PostTag,
)


class PostSerializer(ModelSerializer):
    """
    Serializer for Post model
    """
    class Meta:
        model = Post
        fields = (
            "id", "author", "community",
            "content", "pinned", "created_at",
            "updated_at", "deleted_at",                
        )
        read_only_fields = (
            "id", "author", "created_at", 
            "updated_at", "deleted_at",
            )


class CommentSerializer(ModelSerializer):
    """
    Serializer for Comment model
    """
    replies = SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "post", "author", "parent_comment",
            "content", "replies", "created_at",
            "updated_at", "deleted_at",
        )
        read_only_fields = (
            "id", "author", "created_at", 
            "updated_at", "deleted_at",
            )
    def get_replies(self, obj) -> list[dict]:
        qs = obj.replies.all()
        return CommentSerializer(qs, many=True).data
    

class ReactionSerializer(ModelSerializer):
    """
    Serializer for Reaction model
    """
    class Meta:
        model = Reaction
        fields = (
            "id", "user", "post",
            "comment", "reaction_type", "created_at",
        )
        read_only_fields = ("id", "user", "created_at",)

    def validate(self, attrs):
        if not attrs.get("post") and not attrs.get("comment"):
            raise ValidationError(
                "Reaction must be linked to post or comment"
            )
        return attrs
    

class PollOptionSerializer(ModelSerializer):
    """
    Serializer for PollOption model
    """    
    class Meta:
        model = PollOption
        fields = ("id", "option_text", "votes_count",)
        read_only_fields = ("id", "votes_count",)


class PoleVoteSerializer(ModelSerializer):
    """
    Serializer for PollVote model
    """ 
    class Meta:
        model = PollVote
        fields = ("id", "option", "user", "voted_at",)
        read_only_fields = ("id", "user", "voted_at",)


class PollSerailizer(ModelSerializer):
    """
    Serializer for Poll model
    """
    options = PollOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = (
            "id", "post", "question",
            "expires_at", "allow_multiple", "options",
        )
        read_only_fields = ("id",)


class HashtagSerializer(ModelSerializer):
    """
    Serializer for Hashtag model
    """
    class Meta:
        model = Hashtag
        fields = ("id", "name", "created_at",)
        read_only_fields = ("id", "created_at",)


class PostHashtagSerializer(ModelSerializer):
    """
    Serializer for PostHashtag model
    """
    class Meta:
        model = PostHashtag
        fields = ("id", "post", "hashtag",)
        read_only_fields = ("id",)

    
class TagSerializer(ModelSerializer):
    """
    Serializer for Tag model
    """
    class Meta:
        model = Tag
        fields = ("id", "name",)
        read_only_fields = ("id",)


class PostTagSerializer(ModelSerializer):
    """
    Serializer for PostTag model
    """
    class Meta:
        model = PostTag
        fields = ("id", "post", "tag",)
        read_only_fields = ("id",)
