# DJANGO MODULES

from django.urls import path

# PROJECT MODULES
from .views import CustomTokenObtainPairView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", CustomTokenObtainPairView.as_view()),
]
