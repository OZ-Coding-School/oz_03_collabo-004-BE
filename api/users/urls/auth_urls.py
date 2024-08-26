from django.urls import path

from ..views.google_auth_views import UserGoogleTokenReceiver
from ..views.user_auth_views import (
    UserDeleteView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserTokenRefreshView,
    UserTokenVerifyView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user_register"),
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("google/receiver/", UserGoogleTokenReceiver.as_view(), name="google_receiver"),
    path("token/verify/", UserTokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", UserLogoutView.as_view(), name="user_logout"),
    path("delete/", UserDeleteView.as_view(), name="user_delete"),
]
