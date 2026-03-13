from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserViewSet,
    ProfileViewSet,
    FriendshipViewSet,
    UserBlockViewSet,
    ActivityLogViewSet,
    ReportViewSet,
)

router = DefaultRouter()

router.register("users", UserViewSet, basename="users")
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("friendships", FriendshipViewSet, basename="friendships")
router.register("user-blocks", UserBlockViewSet, basename="user-blocks")
router.register("activity-logs", ActivityLogViewSet, basename="activity-logs")
router.register("reports", ReportViewSet, basename="reports")

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", CustomTokenObtainPairView.as_view()),
    path("", include(router.urls)),
]
