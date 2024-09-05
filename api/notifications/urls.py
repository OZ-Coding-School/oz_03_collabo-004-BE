from django.urls import path

from .views import (
    NotificationDeleteView,
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAsReadView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path(
        "<int:pk>/read/",
        NotificationMarkAsReadView.as_view(),
        name="notification-mark-as-read",
    ),
    path(
        "<int:pk>/delete/", NotificationDeleteView.as_view(), name="notification-delete"
    ),
]
