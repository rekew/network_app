# DJANGO MODULES

from django.urls import path

# PROJECT MODULES

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", CustomTokenObtainPairView.as_view()),

    path("users/<int:id>/", UserDetailView.as_view()),
    path("users/<int:id>/update/", UserUpdateView.as_view()),
    path("users/<int:id>/delete/", UserDeleteView.as_view())
]
