import os
from dataclasses import dataclass, field
from pathlib import Path

import pytz
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from dotenv import load_dotenv
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import RefreshToken

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class GoogleEnvironments:
    """
    init=False : __post_init__ 함수를 호출할 수 있다.
    repr=False : 객체를 print로 찍을 때 해당 필드 데이터는 보이지 않게 됨
    """

    _google_client_id: str = field(init=False, repr=False)
    _google_client_secret: str = field(init=False, repr=False)
    _main_domain: str = field(init=False, repr=False)
    # _google_state: str = field(init=False, repr=False)

    def __post_init__(self):
        # 기능은 init과 동일
        # dataclass에서 자동으로 생성한 init이 __post_init__을 호출해준다.
        self._google_client_id = self.get_env_variable("GOOGLE_CLIENT_ID")
        self._google_client_secret = self.get_env_variable("GOOGLE_CLIENT_SECRET")
        self._main_domain = self.get_env_variable("MAIN_DOMAIN")
        # self._google_state = self.get_env_variable("GOOGLE_CSRF_STATE")

    @staticmethod
    def get_env_variable(name):
        value = os.getenv(name)
        if not value:
            raise ImproperlyConfigured(f"{name} is not set")
        return value

    @property
    def google_client_id(self):
        return self._google_client_id

    @property
    def google_client_secret(self):
        return self._google_client_secret

    @property
    def main_domain(self):
        return self._main_domain

    @property
    def google_state(self):
        return self._google_state


class HunsooKingAuthClass:
    """
    1. Generate ACCESS_TOKEN, REFRESH_TOKEN
    2. Cookie settings
    """

    def __init__(self):
        self._seoul_timezone = pytz.timezone("Asia/Seoul")

        self._access_expiration = (
            timezone.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        ).astimezone(self._seoul_timezone)

        self._refresh_expiration = (
            timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        ).astimezone(self._seoul_timezone)

    def set_jwt_auth_cookie(self, response, jwt_tokens):
        """
        Access token, Refresh token 쿠키 설정 함수
        """
        response = self.set_cookie_attributes(
            response=response,
            key="access",
            token=jwt_tokens["access"],
        )
        response = self.set_cookie_attributes(
            response=response,
            key="refresh",
            token=jwt_tokens["refresh"],
        )

        return response

    @staticmethod
    def set_cookie_attributes(response, key, token):
        """
        Cookie 속성 설정 함수
        key: access or refresh
        token: jwt token
        """
        if key == "access":
            expires_at = HunsooKingAuthClass()._access_expiration
        elif key == "refresh":
            expires_at = HunsooKingAuthClass()._refresh_expiration
        else:
            raise ValueError("key should be 'access' or 'refresh'")

        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            samesite="None",
            secure=True,
            expires=expires_at,
            domain=os.getenv("COOKIE_DOMAIN"),
            path="/",
        )

        return response

    @staticmethod
    def new_access_token_for_user(refresh_token):
        """
        기존 Refresh token을 사용하여 새로운 access token을 생성하는 함수
        이때, 새로 생성된 access token에는, user_id이 정보가 없는데, 직접 payload에 추가해주어야함
        """
        token = RefreshToken(refresh_token)
        new_access_token = token.access_token
        new_access_token["user_id"] = token["user_id"]

        return str(new_access_token)

    @staticmethod
    def set_auth_tokens_for_user(user):
        """
        사용자 인증 전용 JWT 생성 함수
        """
        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = user.id
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def set_new_access_token_for_user(refresh_token):
        """
        기존 Refresh token을 사용하여 새로운 access token을 생성하는 함수
        이때, 새로 생성된 access token에는, user_uuid가 정보가 없는데, 직접 payload에 추가해주어야함
        """
        token = RefreshToken(refresh_token)
        new_access_token = token.access_token
        new_access_token["user_id"] = token["user_id"]
        return str(new_access_token)


class IsAdminUser(BasePermission):
    """
    DRF의 BasePermission 클래스를 상속받아, 관리자에게만 접근권한 허용
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_superuser and request.user.is_active
        )


class GeneralAuthClass:
    """
    일반 로그인 전용 JWT 생성 및 쿠키 설정 클래스
    """

    def __init__(self):
        self._seoul_timezone = pytz.timezone("Asia/Seoul")

        self._access_expiration = (
            timezone.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        ).astimezone(self._seoul_timezone)

        self._refresh_expiration = (
            timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        ).astimezone(self._seoul_timezone)

    def set_jwt_auth_cookie(self, response, jwt_tokens):
        response = self.set_cookie_attributes(
            response=response,
            key="access",
            token=jwt_tokens["access"],
        )
        response = self.set_cookie_attributes(
            response=response,
            key="refresh",
            token=jwt_tokens["refresh"],
        )
        return response

    @staticmethod
    def set_cookie_attributes(response, key, token):
        if key == "access":
            expires_at = GeneralAuthClass()._access_expiration
        elif key == "refresh":
            expires_at = GeneralAuthClass()._refresh_expiration
        else:
            raise ValueError("key should be 'access' or 'refresh'")

        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            samesite="None",
            secure=True,
            expires=expires_at,
            domain=os.getenv("COOKIE_DOMAIN"),
            path="/",
        )
        return response

    @staticmethod
    def set_auth_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = user.id
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
