# Django Modules
from django.db.models import (
    Model, CharField, TextField,
    ForeignKey, CASCADE, BooleanField,
    DateTimeField, OneToOneField, PositiveIntegerField
)

# Project Modules
from apps.abstracts.models import Abstract
from apps.auths.models import CustomUser
from apps.communities.models import Community


class Post(Abstract):

    author = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='posts'
    )

    community = ForeignKey(
        Community,
        on_delete=CASCADE,
        related_name="posts"
    )

    content = TextField()

    pinned = BooleanField(
        default=False,
    )


class Comment(Abstract):

    post = ForeignKey(
        Post,
        on_delete=CASCADE,
        related_name="comments",
    )

    author = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )

    parent_comment = ForeignKey(
        "self",
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    content = TextField()


class Reaction(Model):
    REACTION_CHOICES = [
        ("like", "Like"),
        ("love", "Love"),
        ("laugh", "Laugh"),
        ("wow", "Wow"),
        ("sad", "Sad"),
        ("angry", "Angry"),
    ]
    REACTION_MAX_LENGTH = 10

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )

    post = ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )

    comment = ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )

    reaction_type = CharField(
        max_length=REACTION_MAX_LENGTH,
        choices=REACTION_CHOICES,
    )

    created_at = DateTimeField(
        auto_now_add=True,
    )


class Poll(Model):

    QUESTION_MAX_LENGTH = 255

    post = OneToOneField(
        Post,
        on_delete=CASCADE,
        related_name="poll"
    )

    question = CharField(
        max_length=QUESTION_MAX_LENGTH,
    )

    expires_at = DateTimeField()

    allow_multiple = BooleanField(
        default=False,
    )


class PollOption(Model):

    OPTION_MAX_LENGTH=255

    poll = ForeignKey(
        Poll,
        on_delete=CASCADE,
        related_name="options",
    )

    option_text = CharField(
        max_length=OPTION_MAX_LENGTH,

    )

    votes_count = PositiveIntegerField(
        default=0,
    )


class PollVote(Model):

    poll = ForeignKey(
        Poll,
        on_delete=CASCADE,
        related_name="votes",
    )

    option = ForeignKey(
        PollOption,
        on_delete=CASCADE,
        related_name="votes",
    )

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
    )

    voted_at = DateTimeField(
        auto_now_add=True,
    )


class Hashtag(Model):
    HASHTAG_MAX_LENGTH=255

    name = CharField(
        max_length=HASHTAG_MAX_LENGTH,
        unique=True,
    )

    created_at = DateTimeField(
        auto_now_add=True,
    )


class PostHashtag(Model):
    post = ForeignKey(
        Post,
        on_delete=CASCADE,
        related_name="post_hashtags",
    )

    hashtag = ForeignKey(
        Hashtag,
        on_delete=CASCADE,
        related_name="post_hashtags",
    )


class Tag(Model):

    TAG_MAX_LENGTH=100

    name = CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
    )


class PostTag(Model):

    post = ForeignKey(
        Post,
        on_delete=CASCADE,
        related_name="post_tags",
    )

    tag = ForeignKey(
        Tag,
        on_delete=CASCADE,
        related_name="post_tags",
    )
