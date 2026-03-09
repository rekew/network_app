# Django modules
from django.urls import path, include
# DRF modules
from rest_framework.routers import DefaultRouter
# Project modules
from .views import (
    PostViewSet,
    CommentViewSet,
    ReactionViewSet,
    TagViewSet,
    PostTagViewSet,
    HashtagViewSet,
    PostHashtagViewSet,
    PollViewSet,
)

router: DefaultRouter = DefaultRouter()

router.register(prefix="posts", viewset=PostViewSet, basename="posts")
router.register(prefix="comments", viewset=CommentViewSet, basename="comments")
router.register(prefix="reactions", viewset=ReactionViewSet, basename="reactions")
router.register(prefix="tags", viewset=TagViewSet, basename="tags")
router.register(prefix="post-tags", viewset=PostTagViewSet, basename="post-tags")
router.register(prefix="hashtags", viewset=HashtagViewSet, basename="hashtags")
router.register(prefix="post-hashtags", viewset=PostHashtagViewSet, basename="post-hashtags")
router.register(prefix="polls", viewset=PollViewSet, basename="polls")

urlpatterns = [
    path("", include(router.urls)),
]






