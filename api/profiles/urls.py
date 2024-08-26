from django.urls import path

from .views.profile_auth_views import (
    UserLevelUpdate,
    UserProfileDetailView,
    UserProfileUpdateView,
)
from .views.profile_image_views import DeleteProfileImageView, UpdateProfileImageView
from .views.profile_public_views import PublicUserProfileView

urlpatterns = [
    path("profile/", UserProfileDetailView.as_view(), name="profile-detail"),
    path("profile/update/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("level/", UserLevelUpdate.as_view(), name="update-hunsoo-level"),
    path(
        "profile/image/", UpdateProfileImageView.as_view(), name="profile-image-update"
    ),
    path(
        "profile/image/delete/",
        DeleteProfileImageView.as_view(),
        name="profile-image-delete",
    ),
    path(
        "profile/<str:username>/",
        PublicUserProfileView.as_view(),
        name="public-profile",
    ),
]
