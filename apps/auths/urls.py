# DJANGO MODULES

from django.urls import path

# PROJECT MODULES

from .views import (
    CustomTokenObtainPairView,
    ProfileCreateView,
    ProfileDeleteView,
    ProfileDetailView,
    ProfileUpdateView,
    RegisterView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
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
    path("profiles/create/",          ProfileCreateView.as_view()),
    path("profiles/<int:id>/",        ProfileDetailView.as_view()),
    path("profiles/<int:id>/update/", ProfileUpdateView.as_view()),
    path("profiles/<int:id>/delete/", ProfileDeleteView.as_view()),
]
