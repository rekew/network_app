"""
ASGI config for birlik project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from settings.conf import ENV_ID

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

#Websocket URLS
from apps.notifications.routing import websocket_urlpatterns

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    f"settings.env.{ENV_ID}"
)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )
})
