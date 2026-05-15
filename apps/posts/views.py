# Python Modules
from typing import Any

# Django Modules
from django.utils import timezone

# Django Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse

# DRF-spectacular modules
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

# Project modules
from apps.posts.models import (
    Post, Comment, Reaction,
    Poll, PollOption, PollVote,
    Hashtag, PostHashtag,
    Tag, PostTag,
)
from apps.posts.serializers import (
    PostHashtagSerializer, PostSerializer, CommentSerializer, PostTagSerializer,
    ReactionSerializer, PollOptionSerializer,
    PoleVoteSerializer, PollSerailizer,
    HashtagSerializer, PostHashtag,
    TagSerializer, PostTag,
)
from apps.notifications.services import (
    dispatch_comment_notifications,
    dispatch_post_comment_event,
)


WRITE_ACTION = ("create", "update", "partial_update", "destroy")

ID_PARAM = OpenApiParameter(
    name="id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description="Object ID",
)


def get_permissions_by_action(action):
    if action in WRITE_ACTION:
        return [IsAuthenticated()]
    return [AllowAny()]


@extend_schema(tags=["Posts"])
class PostViewSet(ViewSet):
    """ViewSet for Post model"""

    serializer_class = PostSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(responses={HTTP_200_OK: PostSerializer(many=True)})
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all posts"""
        queryset = Post.objects.select_related("author", "community").filter(deleted_at__isnull=True)
        serializer: PostSerializer = PostSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: PostSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get post by id"""
        post = Post.objects.filter(pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PostSerializer = PostSerializer(post)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=PostSerializer, responses={HTTP_201_CREATED: PostSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new post"""
        serializer: PostSerializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], request=PostSerializer, responses={HTTP_200_OK: PostSerializer})
    def update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Update post"""
        post = Post.objects.filter(pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PostSerializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], request=PostSerializer, responses={HTTP_200_OK: PostSerializer})
    def partial_update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update post"""
        post = Post.objects.filter(pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PostSerializer = PostSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Soft delete post"""
        post = Post.objects.filter(pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)

        post.deleted_at = timezone.now()
        post.save()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Comments"])
class CommentViewSet(ViewSet):
    """ViewSet for Comment model"""

    serializer_class = CommentSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(
        responses={HTTP_200_OK: CommentSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"),
        ]
    )
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all comments"""
        queryset = Comment.objects.select_related("author", "post").filter(deleted_at__isnull=True)
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer: CommentSerializer = CommentSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: CommentSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get comment by id"""
        comment = Comment.objects.filter(pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not comment:
            return DRFResponse({'detail': 'Comment not found'}, status=HTTP_404_NOT_FOUND)

        serializer: CommentSerializer = CommentSerializer(comment)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=CommentSerializer, responses={HTTP_201_CREATED: CommentSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new comment"""
        serializer: CommentSerializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(author=request.user)
        dispatch_post_comment_event(comment, action='created')
        dispatch_comment_notifications(comment)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], request=CommentSerializer, responses={HTTP_200_OK: CommentSerializer})
    def update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Update comment"""
        comment = Comment.objects.filter(pk=kwargs['pk']).first()
        if not comment:
            return DRFResponse({'detail': 'Comment not found'}, status=HTTP_404_NOT_FOUND)

        serializer: CommentSerializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        dispatch_post_comment_event(comment, action='updated')
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], request=CommentSerializer, responses={HTTP_200_OK: CommentSerializer})
    def partial_update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update comment"""
        comment = Comment.objects.filter(pk=kwargs['pk']).first()
        if not comment:
            return DRFResponse({'detail': 'Comment not found'}, status=HTTP_404_NOT_FOUND)

        serializer: CommentSerializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        dispatch_post_comment_event(comment, action='updated')
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Soft delete comment"""
        comment = Comment.objects.filter(pk=kwargs['pk']).first()
        if not comment:
            return DRFResponse({'detail': 'Comment not found'}, status=HTTP_404_NOT_FOUND)

        comment.deleted_at = timezone.now()
        comment.save()
        dispatch_post_comment_event(comment, action='deleted')
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Reactions"])
class ReactionViewSet(ViewSet):
    """ViewSet for Reaction model"""

    serializer_class = ReactionSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(
        responses={HTTP_200_OK: ReactionSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
            OpenApiParameter(
                name="Comment", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by comment ID"
            ),
        ]
    )
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all reactions"""
        queryset = Reaction.objects.select_related("user", "post", "comment").all()
        post_id = request.query_params.get("post")
        comment_id = request.query_params.get("comment")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        if comment_id:
            queryset = queryset.filter(comment_id=comment_id)
        serializer: ReactionSerializer = ReactionSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: ReactionSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get reaction by id"""
        reaction = Reaction.objects.filter(pk=kwargs['pk']).first()
        if not reaction:
            return DRFResponse({'detail': 'Reaction not found'}, status=HTTP_404_NOT_FOUND)

        serializer: ReactionSerializer = ReactionSerializer(reaction)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=ReactionSerializer, responses={HTTP_201_CREATED: ReactionSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new reaction"""
        serializer: ReactionSerializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], request=ReactionSerializer, responses={HTTP_200_OK: ReactionSerializer})
    def update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Update reaction"""
        reaction = Reaction.objects.filter(pk=kwargs['pk']).first()
        if not reaction:
            return DRFResponse({'detail': 'Reaction not found'}, status=HTTP_404_NOT_FOUND)

        serializer: ReactionSerializer = ReactionSerializer(reaction, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], request=ReactionSerializer, responses={HTTP_200_OK: ReactionSerializer})
    def partial_update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update reaction"""
        reaction = Reaction.objects.filter(pk=kwargs['pk']).first()
        if not reaction:
            return DRFResponse({'detail': 'Reaction not found'}, status=HTTP_404_NOT_FOUND)

        serializer: ReactionSerializer = ReactionSerializer(reaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Delete reaction"""
        reaction = Reaction.objects.filter(pk=kwargs['pk']).first()
        if not reaction:
            return DRFResponse({'detail': 'Reaction not found'}, status=HTTP_404_NOT_FOUND)

        reaction.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Tags"])
class TagViewSet(ViewSet):
    """ViewSet for Tag model"""

    serializer_class = TagSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(responses={HTTP_200_OK: TagSerializer(many=True)})
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all tags"""
        queryset = Tag.objects.all()
        serializer: TagSerializer = TagSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: TagSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get tag by id"""
        tag = Tag.objects.filter(pk=kwargs['pk']).first()
        if not tag:
            return DRFResponse({'detail': 'Tag not found'}, status=HTTP_404_NOT_FOUND)

        serializer: TagSerializer = TagSerializer(tag)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=TagSerializer, responses={HTTP_201_CREATED: TagSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new tag"""
        serializer: TagSerializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Delete tag"""
        tag = Tag.objects.filter(pk=kwargs['pk']).first()
        if not tag:
            return DRFResponse({'detail': 'Tag not found'}, status=HTTP_404_NOT_FOUND)

        tag.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Post Tags"])
class PostTagViewSet(ViewSet):
    """ViewSet for PostTag model"""

    serializer_class = PostTagSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(
        responses={HTTP_200_OK: PostTagSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
        ]
    )
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all post tags"""
        queryset = PostTag.objects.select_related("post", "tag").all()
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer: PostTagSerializer = PostTagSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: PostTagSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get post tag by id"""
        post_tag = PostTag.objects.filter(pk=kwargs['pk']).first()
        if not post_tag:
            return DRFResponse({'detail': 'PostTag not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PostTagSerializer = PostTagSerializer(post_tag)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=TagSerializer, responses={HTTP_201_CREATED: PostTagSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new post tag"""
        serializer: PostTagSerializer = PostTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Delete post tag"""
        post_tag = PostTag.objects.filter(pk=kwargs['pk']).first()
        if not post_tag:
            return DRFResponse({'detail': 'PostTag not found'}, status=HTTP_404_NOT_FOUND)

        post_tag.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Hashtags"])
class HashtagViewSet(ViewSet):
    """ViewSet for Hashtag model"""

    serializer_class = HashtagSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(responses={HTTP_200_OK: HashtagSerializer(many=True)})
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all hashtags"""
        queryset = Hashtag.objects.all()
        serializer: HashtagSerializer = HashtagSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: HashtagSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get hashtag by id"""
        hashtag = Hashtag.objects.filter(pk=kwargs['pk']).first()
        if not hashtag:
            return DRFResponse({'detail': 'Hashtag not found'}, status=HTTP_404_NOT_FOUND)

        serializer: HashtagSerializer = HashtagSerializer(hashtag)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=TagSerializer, responses={HTTP_201_CREATED: HashtagSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new hashtag"""
        serializer: HashtagSerializer = HashtagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)


@extend_schema(tags=["Post Hashtags"])
class PostHashtagViewSet(ViewSet):
    """ViewSet for PostHashtag model"""

    serializer_class = PostHashtagSerializer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(
        responses={HTTP_200_OK: PostHashtagSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
        ]
    )
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all post hashtags"""
        queryset = PostHashtag.objects.select_related("post", "hashtag").all()
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer: PostHashtagSerializer = PostHashtagSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: PostHashtagSerializer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get post hashtag by id"""
        post_hashtag = PostHashtag.objects.filter(pk=kwargs['pk']).first()
        if not post_hashtag:
            return DRFResponse({'detail': 'PostHashtag not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PostHashtagSerializer = PostHashtagSerializer(post_hashtag)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=TagSerializer, responses={HTTP_201_CREATED: PostHashtagSerializer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new post hashtag"""
        serializer: PostHashtagSerializer = PostHashtagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Delete post hashtag"""
        post_hashtag = PostHashtag.objects.filter(pk=kwargs['pk']).first()
        if not post_hashtag:
            return DRFResponse({'detail': 'PostHashtag not found'}, status=HTTP_404_NOT_FOUND)

        post_hashtag.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Polls"])
class PollViewSet(ViewSet):
    """ViewSet for Poll model"""

    serializer_class = PollSerailizer

    def get_permissions(self):
        return get_permissions_by_action(self.action)

    @extend_schema(responses={HTTP_200_OK: PollSerailizer(many=True)})
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all polls"""
        queryset = Poll.objects.select_related("post").prefetch_related("options").all()
        serializer: PollSerailizer = PollSerailizer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_200_OK: PollSerailizer})
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get poll by id"""
        poll = Poll.objects.filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PollSerailizer = PollSerailizer(poll)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(request=PollSerailizer, responses={HTTP_201_CREATED: PollSerailizer})
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new poll"""
        serializer: PollSerailizer = PollSerailizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(parameters=[ID_PARAM], request=PollSerailizer, responses={HTTP_200_OK: PollSerailizer})
    def update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Update poll"""
        poll = Poll.objects.filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PollSerailizer = PollSerailizer(poll, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], request=PollSerailizer, responses={HTTP_200_OK: PollSerailizer})
    def partial_update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update poll"""
        poll = Poll.objects.filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PollSerailizer = PollSerailizer(poll, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(parameters=[ID_PARAM], responses={HTTP_204_NO_CONTENT: None})
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Delete poll"""
        poll = Poll.objects.filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)

        poll.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)