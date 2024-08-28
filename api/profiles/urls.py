from django.urls import path

from .views.profile_auth_views import (
    UserLevelUpdate,
    UserProfileDetailView,
    UserProfileUpdateView,
)
from .views.profile_image_views import DeleteProfileImageView, UpdateProfileImageView

urlpatterns = [
    path("profile/", UserProfileDetailView.as_view(), name="user-profile-detail"),
    path(
        "profile/<str:username>/",
        UserProfileDetailView.as_view(),
        name="user-profile-detail-other",
    ),
    path("profile/update/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("level/<int:id>/", UserLevelUpdate.as_view(), name="update-hunsoo-level"),
    path(
        "profile/image/", UpdateProfileImageView.as_view(), name="profile-image-update"
    ),
    path(
        "profile/image/delete/",
        DeleteProfileImageView.as_view(),
        name="profile-image-delete",
    ),
]
