from django.urls import path
from users.views.google_auth_view import UserGoogleTokenReceiver
from users.views.user_auth_view import (
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
    path("google/receiver", UserGoogleTokenReceiver.as_view(), name="google_receiver"),
    path("token/verify", UserTokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", UserLogoutView.as_view(), name="user_logout"),
    path("delete", UserDeleteView.as_view(), name="user_delete"),
]
