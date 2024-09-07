from django.urls import path

from ..views.google_auth_views import UserGoogleTokenReceiver
from ..views.user_auth_views import (
    LoginStatusView,
    SendPasswordResetEmailView,
    SendVerificationEmailView,
    UserDeleteView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserStatusView,
    UserTokenRefreshView,
    UserTokenVerifyView,
    verification_failed,
    verification_success,
    verify_email,
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
    path(
        "email/verification/",
        SendVerificationEmailView.as_view(),
        name="send_verification_email",
    ),
    path(
        "email/password/",
        SendPasswordResetEmailView.as_view(),
        name="send_password_reset_email",
    ),
    path("verify-email/<uidb64>/<token>/", verify_email, name="verify_email"),
    path("verification-failed/", verification_failed, name="verification_failed"),
    path("verification-success/", verification_success, name="verification_success"),
]
