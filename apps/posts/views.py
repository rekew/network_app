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
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse

# DRF-spectacular modules
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

# Project modules
from apps.posts.permissions import (
    IsAuthor,
    IsReactionOwner,
    IsPostAuthor,
    IsAdminOrReadOnly,
)
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

ERROR_404 = OpenApiResponse(
    description="Object not found",
)
ERROR_401 = OpenApiResponse(
    description="Authentication credentials were not provided or are invalid",
)
ERROR_400 = OpenApiResponse(
    description="Bad Request",
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
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAuthor()]
        return [AllowAny()]

    @extend_schema(
        summary="List all posts",
        description="Retrieve a list of all posts. "
        "Optional query parameters can be used to filter the results.",
        responses={HTTP_200_OK: PostSerializer(many=True)})
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all posts"""
        queryset = Post.objects.select_related(
            "author", "community").filter(deleted_at__isnull=True)
        serializer: PostSerializer = PostSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a post",
        description="Retrieve a single post by its ID.",
        parameters=[ID_PARAM],
        responses={
                HTTP_200_OK: PostSerializer,
                HTTP_404_NOT_FOUND: ERROR_404,
        })
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get post by id"""
        post = Post.objects.filter(
            pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)

        serializer: PostSerializer = PostSerializer(post)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Create a new post",
        description="Create a new post. The author is automatically set to the authenticated user.",
        request=PostSerializer,
        responses={
                HTTP_201_CREATED: PostSerializer,
                HTTP_400_BAD_REQUEST: ERROR_400,
                HTTP_401_UNAUTHORIZED: ERROR_401,
        })
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

    @extend_schema(
        summary="Update a post",
        description="Fully updates an existing post. All fields are required.",
        parameters=[ID_PARAM],
        request=PostSerializer,
        responses={
            HTTP_200_OK: PostSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
    def update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Update post"""
        post = Post.objects.filter(
            pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        serializer: PostSerializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Partially update a post",
        description="Partially updates an existing post. Only the provided fields will be updated.",
        parameters=[ID_PARAM],
        request=PostSerializer,
        responses={
            HTTP_200_OK: PostSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        }
    )
    def partial_update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update post"""
        post = Post.objects.filter(
            pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        serializer: PostSerializer = PostSerializer(
            post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Delete a post",
        description="Soft delete a post by setting the deleted_at field to the current timestamp.",
        parameters=[ID_PARAM],
        responses={
                HTTP_204_NO_CONTENT: None,
                HTTP_400_BAD_REQUEST: ERROR_400,
                HTTP_404_NOT_FOUND: ERROR_404,
        })
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Soft delete post"""
        post = Post.objects.filter(
            pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not post:
            return DRFResponse({'detail': 'Post not found'}, status=HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        post.deleted_at = timezone.now()
        post.save()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Comments"])
class CommentViewSet(ViewSet):
    """ViewSet for Comment model"""

    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAuthor()]
        return [AllowAny()]

    @extend_schema(
        summary="List all comments",
        description="Returns a list of all non-deleted comments."
        "Can be filtered by post ID using the 'post' query parameter.",
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"),
        ],
        responses={HTTP_200_OK: CommentSerializer(many=True)},

    )
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all comments"""
        queryset = Comment.objects.select_related(
            "author", "post").filter(deleted_at__isnull=True)
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer: CommentSerializer = CommentSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a comment",
        description="Retrieve a single comment by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: CommentSerializer,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get comment by id"""
        comment = Comment.objects.filter(
            pk=kwargs['pk'], deleted_at__isnull=True).first()
        if not comment:
            return DRFResponse({'detail': 'Comment not found'}, status=HTTP_404_NOT_FOUND)

        serializer: CommentSerializer = CommentSerializer(comment)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Create a new comment",
        description="Create a new comment on post. The author is automatically set to the authenticated user.",
        request=CommentSerializer,
        responses={
            HTTP_201_CREATED: CommentSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        })
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

    @extend_schema(
        summary="Update a comment",
        description="Update an existing comment by its ID.",
        parameters=[ID_PARAM],
        request=CommentSerializer,
        responses={
            HTTP_200_OK: CommentSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        }
    )
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
        self.check_object_permissions(request, comment)

        serializer: CommentSerializer = CommentSerializer(
            comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        dispatch_post_comment_event(comment, action='updated')
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Partially update a comment",
        description="Partially update an existing comment by its ID.",
        parameters=[ID_PARAM],
        request=CommentSerializer,
        responses={
            HTTP_200_OK: CommentSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        }
    )
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
        self.check_object_permissions(request, comment)

        serializer: CommentSerializer = CommentSerializer(
            comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        dispatch_post_comment_event(comment, action='updated')
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Delete a comment",
        description="Soft delete an existing comment by its ID setting its deleted_at timestamp",
        parameters=[ID_PARAM],
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        }
    )
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
        self.check_object_permissions(request, comment)

        comment.deleted_at = timezone.now()
        comment.save()
        dispatch_post_comment_event(comment, action='deleted')
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Reactions"])
class ReactionViewSet(ViewSet):
    """ViewSet for Reaction model"""

    serializer_class = ReactionSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsReactionOwner()]
        return [AllowAny()]

    @extend_schema(
        summary="List reactions",
        description="Get all reactions.",
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
            OpenApiParameter(
                name="Comment", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by comment ID"
            ),
        ],
        responses={HTTP_200_OK: ReactionSerializer(many=True)},
    )
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all reactions"""
        queryset = Reaction.objects.select_related(
            "user", "post", "comment").all()
        post_id = request.query_params.get("post")
        comment_id = request.query_params.get("comment")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        if comment_id:
            queryset = queryset.filter(comment_id=comment_id)
        serializer: ReactionSerializer = ReactionSerializer(
            queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a reaction",
        description="Returns a single reaction by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: ReactionSerializer,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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

    @extend_schema(
        summary="Create a reaction",
        description="Create a new reaction. The user is automatically set to the authenticated user.",
        request=ReactionSerializer,
        responses={
            HTTP_201_CREATED: ReactionSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        })
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

    @extend_schema(
        summary="Update a reaction",
        description="Update an existing reaction by its ID. All fields are required",
        parameters=[ID_PARAM],
        request=ReactionSerializer,
        responses={
            HTTP_200_OK: ReactionSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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
        self.check_object_permissions(request, reaction)

        serializer: ReactionSerializer = ReactionSerializer(
            reaction, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Partially update a reaction",
        description="Partially update an existing reaction by its ID. Only the provided fields will be updated.",
        parameters=[ID_PARAM],
        request=ReactionSerializer,
        responses={
            HTTP_200_OK: ReactionSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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
        self.check_object_permissions(request, reaction)

        serializer: ReactionSerializer = ReactionSerializer(
            reaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Delete a reaction",
        description="Permanently delete a reaction by its ID",
        parameters=[ID_PARAM],
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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
        self.check_object_permissions(request, reaction)

        reaction.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


@extend_schema(tags=["Tags"])
class TagViewSet(ViewSet):
    """ViewSet for Tag model"""

    serializer_class = TagSerializer

    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    @extend_schema(
        summary="List all tags",
        description="Get a list of all tags.",
        responses={HTTP_200_OK: TagSerializer(many=True)})
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

    @extend_schema(
        summary="Retrieve a tag",
        description="Returns a single tag by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: TagSerializer,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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

    @extend_schema(
        summary="Create a new tag",
        description="Create a new tag with the provided data. Tag name must be unique",
        request=TagSerializer,
        responses={
            HTTP_201_CREATED: TagSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        }
    )
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

    @extend_schema(
        summary="Delete a tag",
        description="Permanently delete a tag by its ID. Assosciated PostTag objects will also be deleted.",
        parameters=[ID_PARAM],
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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
        summary="List all post-tag relations",
        description="Returns a list of all post-tag relations",
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
        ],
        responses={HTTP_200_OK: PostTagSerializer(many=True)},

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

    @extend_schema(
        summary="Retrieve a post tag",
        description="Returns a single post-tag by its ID",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: PostTagSerializer,
            HTTP_404_NOT_FOUND: ERROR_404,
        }
    )
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

    @extend_schema(
        summary="Attach a tag to a post",
        description="Creates a relation between a post and a tag",
        request=TagSerializer,
        responses={
            HTTP_201_CREATED: PostTagSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        }
    )
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

    @extend_schema(
        summary="Detach a tag from a post",
        description="Permanently deletes the relation between a post and a tag by its ID",
        parameters=[ID_PARAM],
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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
        return [IsAdminOrReadOnly()]

    @extend_schema(
        summary="List all hashtags",
        description="Get a list of all hashtags.",
        responses={HTTP_200_OK: HashtagSerializer(many=True)})
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

    @extend_schema(
        summary="Retrieve a hashtag",
        description="Returns a single hashtag by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: HashtagSerializer,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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

    @extend_schema(
        summary="Create a new hashtag",
        description="Creates a new hashtag. Hashtag name must be unique.",
        request=TagSerializer,
        responses={
            HTTP_201_CREATED: HashtagSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        }
    )
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
        summary="List all post-hashtag relations",
        description="Returns a list of all post-hashtag relations",
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
        ],
        responses={HTTP_200_OK: PostHashtagSerializer(many=True)},

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
        serializer: PostHashtagSerializer = PostHashtagSerializer(
            queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a post-hashtag relation",
        description="Returns a single post-hashtag relation by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: PostHashtagSerializer,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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

    @extend_schema(
        summary="Attach a hashtag to a post",
        description="Creates a relation between a post and a hashtag",
        request=TagSerializer,
        responses={
            HTTP_201_CREATED: PostHashtagSerializer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        })
    def create(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Create a new post hashtag"""
        serializer: PostHashtagSerializer = PostHashtagSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(
        summary="Delete a post-hashtag relation",
        description="Deletes a single post-hashtag relation by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsPostAuthor()]
        return [AllowAny()]

    @extend_schema(
        summary="List all polls",
        description="Get a list of all polls.",
        responses={HTTP_200_OK: PollSerailizer(many=True)})
    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all polls"""
        queryset = Poll.objects.select_related(
            "post").prefetch_related("options").all()
        serializer: PollSerailizer = PollSerailizer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a poll",
        description="Returns a single poll by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_200_OK: PollSerailizer,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
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

    @extend_schema(
        summary="Create a new poll",
        description="Creates a new poll with the provided data.",
        request=PollSerailizer,
        responses={
            HTTP_201_CREATED: PollSerailizer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
        })
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

    @extend_schema(
        summary="Update a poll",
        description="Updates a single poll by its ID.",
        parameters=[ID_PARAM],
        request=PollSerailizer,
        responses={
            HTTP_200_OK: PollSerailizer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
    def update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Update poll"""
        poll = Poll.objects.select_related("post__author").filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, poll)

        serializer: PollSerailizer = PollSerailizer(poll, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Partially update a poll",
        description="Partially updates a single poll by its ID.",
        parameters=[ID_PARAM],
        request=PollSerailizer,
        responses={
            HTTP_200_OK: PollSerailizer,
            HTTP_400_BAD_REQUEST: ERROR_400,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        })
    def partial_update(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update poll"""
        poll = Poll.objects.select_related("post__author").filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, poll)

        serializer: PollSerailizer = PollSerailizer(
            poll, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Delete a poll",
        description="Deletes a single poll by its ID.",
        parameters=[ID_PARAM],
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: ERROR_401,
            HTTP_404_NOT_FOUND: ERROR_404,
        }
    )
    def destroy(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Delete poll"""
        poll = Poll.objects.select_related("post__author").filter(pk=kwargs['pk']).first()
        if not poll:
            return DRFResponse({'detail': 'Poll not found'}, status=HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, poll)

        poll.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)
