# DJANGO MODULES

from django.urls import path

# PROJECT MODULES

from .views import (
    ActivityLogCreateView,
    ActivityLogListView,
    CustomTokenObtainPairView,
    FriendshipCreateView,
    FriendshipDeleteView,
    FriendshipListView,
    ProfileDeleteView,
    ProfileDetailView,
    ProfileUpdateView,
    RegisterView,
    ReportCreateView,
    ReportDetailView,
    ReportListView,
    UserBlockCreateView,
    UserBlockDeleteView,
    UserBlockListView,
    UserDeleteView,
    UserDetailView,
    UserUpdateView,
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/",    CustomTokenObtainPairView.as_view()),

    # Users
    path("users/<int:id>/",          UserDetailView.as_view()),
    path("users/<int:id>/update/",   UserUpdateView.as_view()),
    path("users/<int:id>/delete/",   UserDeleteView.as_view()),

    # Profiles
    path("profiles/<int:id>/",        ProfileDetailView.as_view()),
    path("profiles/<int:id>/update/", ProfileUpdateView.as_view()),
    path("profiles/<int:id>/delete/", ProfileDeleteView.as_view()),

    # Friendships
    path("friendships/create/",      FriendshipCreateView.as_view()),
    path("friendships/",             FriendshipListView.as_view()),
    path("friendships/<int:id>/delete/", FriendshipDeleteView.as_view()),

    # User blocks
    path("user-blocks/create/",      UserBlockCreateView.as_view()),
    path("user-blocks/",             UserBlockListView.as_view()),
    path("user-blocks/<int:id>/delete/", UserBlockDeleteView.as_view()),

    # Activity logs
    path("activity-logs/create/",    ActivityLogCreateView.as_view()),
    path("activity-logs/",           ActivityLogListView.as_view()),

    # Reports
    path("reports/create/",          ReportCreateView.as_view()),
    path("reports/",                 ReportListView.as_view()),
    path("reports/<int:id>/",        ReportDetailView.as_view()),
]
