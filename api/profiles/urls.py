from django.urls import path

from .views import UserLevelUpdate

urlpatterns = [
    path("level/", UserLevelUpdate.as_view(), name="update-hunsoo-level"),
]
