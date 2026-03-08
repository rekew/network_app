from django.urls import path

from .views import (
    MediaCreateView,
    MediaDeleteView,
    MediaDetailView,
    MediaListView,
)

urlpatterns = [
    path("media/create/", MediaCreateView.as_view()),
    path("media/", MediaListView.as_view()),
    path("media/<int:id>/", MediaDetailView.as_view()),
    path("media/<int:id>/delete/", MediaDeleteView.as_view()),
]

