# Django Channels
from django.urls import re_path
from . import consumers

post_websocket_urlpatterns = [
    re_path(
        r"^ws/comment/(?P<comment_id>[0-9a-f-]+)/reactions/$",
        consumers.CommentReactionConsumer.as_asgi(),
    ),
]