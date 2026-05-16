from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/posts/(?P<post_id>\d+)/comments/$', consumers.PostCommentsConsumer.as_asgi()),
    re_path(r'ws/posts/(?P<post_id>\d+)/typing/$', consumers.PostTypingConsumer.as_asgi()),
    re_path(r'ws/moderation/$', consumers.ModerationConsumer.as_asgi()),
]