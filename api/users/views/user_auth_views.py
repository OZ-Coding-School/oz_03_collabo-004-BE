import os

from common.logger import logger
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from profiles.models import Profile
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.serializers import (
    EmptySerializer,
    UserDeleteSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserRegisterSerializer,
    UserTokenRefreshSerializer,
)
from users.utils import GeneralAuthClass, HunsooKingAuthClass

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    logger.info("User registration attempt")
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info("User registration attempt")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        Profile.objects.create(user=user)

        jwt_tokens = GeneralAuthClass.set_auth_tokens_for_user(user)

        response = Response(
            {
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "access_token": jwt_tokens["access"],
                "refresh_token": jwt_tokens["refresh"],
                "created_at": user.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            status=status.HTTP_201_CREATED,
        )

        response = GeneralAuthClass().set_jwt_auth_cookie(response, jwt_tokens)

        logger.info(f"User {user.email} registered successfully")
        return response


class UserLoginView(APIView):
    authentication_classes = []  # 일반 로그인에서는 별도의 인증 클래스 사용 안 함
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("User login attempt")
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is not None:
            jwt_tokens = GeneralAuthClass.set_auth_tokens_for_user(user)

            response_data = {
                "token": jwt_tokens["access"],
                "user_id": str(user.id),
                "nickname": user.nickname,
            }

            response = Response(response_data, status=status.HTTP_200_OK)
            response = GeneralAuthClass().set_jwt_auth_cookie(response, jwt_tokens)

            logger.info(f"User {user.email} logged in successfully")
            return response
        else:
            logger.error("Invalid credentials provided for login")
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserTokenVerifyView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("POST /api/auth/token/verify")
        token = request.COOKIES.get("access")
        if not token:
            logger.error("/api/auth/token/verify: Access token not found in cookies")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            AccessToken(token)
            logger.info("/api/auth/token/verify: Access token is valid")
            return Response(status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            logger.error("/api/auth/token/verify: Invalid access token")
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserTokenRefreshView(generics.GenericAPIView):
    serializer_class = UserTokenRefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("POST /api/auth/token/refresh")
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            logger.error("/api/auth/token/refresh: Refresh token not found in cookies")
            return Response(
                {"detail": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh_token": refresh_token})
        serializer.is_valid(raise_exception=True)

        try:
            access_token = HunsooKingAuthClass.new_access_token_for_user(
                refresh_token=serializer.validated_data["refresh_token"]
            )
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/token/refresh: {e}")
            return Response(
                data={"error occurs": "UserTokenRefreshView", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            data={"access": access_token, "message": "Token refreshed successfully"}
        )
        try:
            HunsooKingAuthClass.set_cookie_attributes(
                response=response, key="access", token=access_token
            )
        except ValueError:
            logger.error("/api/auth/token/refresh: Failed to set access token cookie")
            return Response(
                {"error occurs": "UserTokenRefreshView"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info("/api/auth/token/refresh: Token refreshed successfully")
        return response


class UserLogoutView(generics.GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={"refresh_token": request.COOKIES.get("refresh")}
        )
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh_token"]
            with transaction.atomic():
                refresh_token.blacklist()
            response = Response(status=status.HTTP_200_OK)
            response.delete_cookie(
                "access", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            response.delete_cookie(
                "refresh", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            logger.info("/api/auth/logout: Logout successful")
            return response
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/logout: {e}")
            return Response(
                data={"message": "Invalid refresh token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"/api/auth/logout: {str(e)}")
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDeleteView(generics.GenericAPIView):
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        logger.info("DELETE /api/auth/delete")
        data = request.data.copy()
        data["refresh_token"] = request.COOKIES.get("refresh")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.validated_data["user"]
            refresh_token = serializer.validated_data["refresh_token"]
            with transaction.atomic():
                user.delete()
                refresh_token.blacklist()
            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie(
                "access", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            response.delete_cookie(
                "refresh", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            logger.info("/api/auth/delete: User deleted successfully")
            return response
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/delete: {e}")
            return Response(
                data={"message": "Invalid refresh token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"/api/auth/delete: {str(e)}")
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 특정유저의 관리자와 일반유저 판단
class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        status = 1 if user.is_superuser or user.is_staff else 0
        return Response({"status": status})


# 로그인 상태 확인
class LoginStatusView(GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        is_authenticated = request.user.is_authenticated
        return Response({"login": is_authenticated})
