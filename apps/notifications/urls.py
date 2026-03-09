from django.urls import path

from .views import (
    NotificationCreateView,
    NotificationDeleteView,
    NotificationDetailView,
    NotificationListView,
)

urlpatterns = [
    path("notifications/create/", NotificationCreateView.as_view()),
    path("notifications/", NotificationListView.as_view()),
    path("notifications/<int:id>/", NotificationDetailView.as_view()),
    path("notifications/<int:id>/delete/", NotificationDeleteView.as_view()),
]

