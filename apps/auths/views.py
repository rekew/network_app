# THIRD PARTY MODULES

from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

# PROJECT MODULES
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
