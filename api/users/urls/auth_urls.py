from django.urls import path

from ..views.google_auth_views import UserGoogleTokenReceiver
from ..views.user_auth_views import (
    LoginStatusView,
    UserDeleteView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserStatusView,
    UserTokenRefreshView,
    UserTokenVerifyView,
)
from ..views.user_find_views import (
    FindUsernameView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user_register"),
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("google/receiver/", UserGoogleTokenReceiver.as_view(), name="google_receiver"),
    path("token/verify/", UserTokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", UserLogoutView.as_view(), name="user_logout"),
    path("delete/", UserDeleteView.as_view(), name="user_delete"),
    path("status/", UserStatusView.as_view(), name="user-status"),
    path("login/status/", LoginStatusView.as_view(), name="user-login-status"),
    path('username/', FindUsernameView.as_view(), name='find_username'),
    path('pwd_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('pwd_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
