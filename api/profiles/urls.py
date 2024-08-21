from django.urls import path

from .views.profile_auth_views import UserProfileDetailView, UserLevelUpdate
from .views.profile_image_views import ProfileImageUpdateView, ProfileImageDeleteView
from .views.profile_public_views import PublicUserProfileView

urlpatterns = [
    path('profile/', UserProfileDetailView.as_view(), name='profile-detail'),
    path("level/", UserLevelUpdate.as_view(), name="update-hunsoo-level"),
    path('profile/image/', ProfileImageUpdateView.as_view(), name='profile-image-update'),
    path('profile/image/delete/', ProfileImageDeleteView.as_view(), name='profile-image-delete'),
    path('profile/<str:username>/', PublicUserProfileView.as_view(), name='public-profile'),
]
