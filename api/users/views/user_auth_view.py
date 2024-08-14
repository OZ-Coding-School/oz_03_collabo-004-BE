import os

from common.logger import logger
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from users.serializers import (
    EmptySerializer,
    UserDeleteSerializer,
    UserLogoutSerializer,
    UserTokenRefreshSerializer,
)
from users.utils import HunsooKingAuthClass


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
        logger.info("POST /api/auth/logout")
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
