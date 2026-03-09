# DRF modules
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)

# Django modules
from django.shortcuts import get_object_or_404
from django.utils import timezone

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


WRITE_ACTION = ("create", "update", "partial_update", "destroy")

def get_permissions_by_action(action):
    if action in WRITE_ACTION:
        return [IsAuthenticated()]
    return [AllowAny()]

@extend_schema(tags=["Posts"])
class PostViewSet(ViewSet):
    """
    ViewSet for Post model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(responses={200: PostSerializer(many=True)})
    def list(self, request):
        queryset = Post.objects.select_related("author", "community").filter(deleted_at__isnull=True)
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: PostSerializer})
    def retrieve(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    @extend_schema(request=PostSerializer, responses={201: PostSerializer})
    def create(self, request):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)
    
    @extend_schema(request=PostSerializer, responses={200: PostSerializer})
    def update(self, request, pk=None):
        post = get_object_or_404(Post,pk=pk, deleted_at__isnull=True)
        serializer = PostSerializer(post,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(request=PostSerializer, responses={200: PostSerializer})
    def partial_update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)
        serializer = PostSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)
        post.deleted_at = timezone.now()
        post.save()
        return Response(status=HTTP_204_NO_CONTENT)
    

@extend_schema(tags=["Comments"])
class CommentViewSet(ViewSet):
    """
    ViewSet for comment model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(
            responses={200: CommentSerializer(many=True)},
            parameters=[
                OpenApiParameter(
                    name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, 
                    description="Filter by post ID"),
            ]
    )
    def list(self, request):
        queryset = Comment.objects.select_related("author", "post").filter(deleted_at__isnull=True)
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: CommentSerializer})
    def retrieve(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk, deleted_at__isnull=True)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    @extend_schema(request=CommentSerializer, responses={201: CommentSerializer})
    def create(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(request=CommentSerializer, responses={200: CommentSerializer})
    def update(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(request=CommentSerializer, responses={200: CommentSerializer})
    def partial_update(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        comment.deleted_at = timezone.now()
        comment.save()
        return Response(status=HTTP_204_NO_CONTENT)
    

@extend_schema(tags=["Reactions"])
class ReactionViewSet(ViewSet):
    """
    ViewSet for Reaction model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(
            responses={200: ReactionSerializer(many=True)},
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
    def list(self, request):
        queryset = Reaction.objects.select_related("user", "post", "comment").all()
        post_id = request.query_params.get("post")
        comment_id = request.query_params.get("comment")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        if comment_id:
            queryset = queryset.filter(comment_id=comment_id)
        serializer = ReactionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: ReactionSerializer})
    def retrieve(self, request, pk=None):
        reaction = get_object_or_404(Reaction, pk=pk)
        serializer = ReactionSerializer(reaction)
        return Response(serializer.data)
    
    @extend_schema(request=ReactionSerializer, responses={201: ReactionSerializer})
    def create(self, request):
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)
    
    @extend_schema(request=ReactionSerializer, responses={200: ReactionSerializer})
    def update(self, request, pk=None):
        reaction = get_object_or_404(Reaction, pk=pk)
        serializer = ReactionSerializer(reaction, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(request=ReactionSerializer, responses={200: ReactionSerializer})
    def partial_update(self, request, pk=None):
        reaction = get_object_or_404(Reaction, pk=pk)
        serializer = ReactionSerializer(reaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        reaction = get_object_or_404(Reaction, pk=pk)
        reaction.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    

@extend_schema(tags=["Tags"])
class TagViewSet(ViewSet):
    """
    ViewSet for Tag model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(responses={200: TagSerializer(many=True)})
    def list(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: TagSerializer})
    def retrieve(self, request, pk=None):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)
    
    @extend_schema(request=TagSerializer, responses={201: TagSerializer})
    def create(self, request):
        serializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    
    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    

@extend_schema(tags=["Post Tags"])
class PostTagViewSet(ViewSet):
    """
    ViewSet for PostTag model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(
            responses={200: PostTagSerializer(many=True)},
            parameters=[
                OpenApiParameter(
                    name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                    description="Filter by post ID"
                    ),
            ]
    )
    def list(self, request):
        queryset = PostTag.objects.select_related("post", "tag").all()
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer = PostTagSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: PostTagSerializer})
    def retrieve(self, request, pk=None):
        post_tag = get_object_or_404(PostTag, pk=pk)
        serializer = PostTagSerializer(post_tag)
        return Response(serializer.data)
    
    @extend_schema(request=TagSerializer, responses={201: PostTagSerializer})
    def create(self, request):
        serializer = PostTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    
    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        post_tag = get_object_or_404(PostTag, pk=pk)
        post_tag.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    

@extend_schema(tags=["Hashtags"])
class HashtagViewSet(ViewSet):
    """
    ViewSet for Hashtag model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(responses={200: HashtagSerializer(many=True)})
    def list(self, request):
        queryset = Hashtag.objects.all()
        serializer = HashtagSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: HashtagSerializer})
    def retrieve(self, request, pk=None):
        hashtag = get_object_or_404(Hashtag, pk=pk)
        serializer = HashtagSerializer(hashtag)
        return Response(serializer.data)
    
    @extend_schema(request=TagSerializer, responses={201: HashtagSerializer})
    def create(self, request):
        serializer = HashtagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    

@extend_schema(tags=["Post Hashtags"])
class PostHashtagViewSet(ViewSet):
    """
    ViewSet for PostHashtag model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(
        responses={200: PostHashtagSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="post", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description="Filter by post ID"
            ),
        ]
    )
    def list(self, request):
        queryset = PostHashtag.objects.select_related("post", "hashtag").all()
        post_id = request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        serializer = PostHashtagSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: PostHashtagSerializer})
    def retrieve(self, request, pk=None):
        post_hashtag = get_object_or_404(PostHashtag, pk=pk)
        serializer = PostHashtagSerializer(post_hashtag)
        return Response(serializer.data)
    
    @extend_schema(request=TagSerializer, responses={201: PostHashtagSerializer})
    def create(self, request):
        serializer = PostHashtagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    
    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        post_hashtag = get_object_or_404(PostHashtag, pk=pk)
        post_hashtag.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    

@extend_schema(tags=["Polls"])
class PollViewSet(ViewSet):
    """
    ViewSet for Poll model
    """
    def get_permissions(self):
        return get_permissions_by_action(self.action)
    
    @extend_schema(responses={200: PollSerailizer(many=True)})
    def list(self, request):
        queryset = Poll.objects.select_related("post").prefetch_related("options").all()
        serializer = PollSerailizer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: PollSerailizer})
    def retrieve(self, request, pk=None):
        poll = get_object_or_404(Poll, pk=pk)
        serializer = PollSerailizer(poll)
        return Response(serializer.data)

    @extend_schema(request=TagSerializer, responses={201: PollSerailizer})
    def create(self, request):
        serializer = PollSerailizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @extend_schema(request=TagSerializer, responses={200: PollSerailizer()})
    def update(self, request, pk=None):
        poll = get_object_or_404(Poll, pk=pk)
        serializer = PollSerailizer(poll, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(request=TagSerializer, responses={200: PollSerailizer})
    def partial_update(self, request, pk=None):
        poll = get_object_or_404(Poll, pk=pk)
        serializer = PollSerailizer(poll, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        poll = get_object_or_404(Poll, pk=pk)
        poll.delete()
        return Response(status=HTTP_204_NO_CONTENT)



