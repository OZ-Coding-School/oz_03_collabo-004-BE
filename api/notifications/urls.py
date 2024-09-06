from django.urls import path

from .views import (
    AdminNotificationDeleteView,
    AdminNotificationDetailView,
    AdminNotificationListView,
    AdminNotificationMarkAsReadView,
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
    path("admin/", AdminNotificationListView.as_view(), name="admin-notification-list"),
    path(
        "<int:pk>/admin/",
        AdminNotificationDetailView.as_view(),
        name="admin-notification-detail",
    ),
    path(
        "<int:pk>/read/admin/",
        AdminNotificationMarkAsReadView.as_view(),
        name="admin-notification-mark-as-read",
    ),
    path(
        "<int:pk>/delete/admin/",
        AdminNotificationDeleteView.as_view(),
        name="admin-notification-delete",
    ),
]
