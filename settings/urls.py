# DJANGO MODULES
from django.contrib import admin
from django.urls import include, path

# THIRD PARTY MODULES
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("apps.auths.urls")),
]
