# Django modules
from django.urls import path, include
# DRF modules
from rest_framework.routers import DefaultRouter
# Project modules
from .views import (
    ChatViewSet
)

router: DefaultRouter = DefaultRouter()

router.register(prefix="chats", viewset=ChatViewSet, basename="chats")

urlpatterns = [
    path("", include(router.urls)),
]






