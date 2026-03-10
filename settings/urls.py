# DJANGO MODULES
from django.contrib import admin
from django.urls import include, path

# THIRD PARTY MODULES
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Project urls
    path('admin/', admin.site.urls),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Apps
    path("api/", include("apps.auths.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("posts/", include("apps.posts.urls")),
    path('communities/', include('apps.communities.urls')),

    # API url docs
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
