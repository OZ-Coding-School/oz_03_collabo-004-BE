from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class EmptySerializer(serializers.Serializer):
    pass


class UserTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")
        if not refresh_token:
            raise serializers.ValidationError({"message": "Refresh token is missing"})

        try:
            # Verify and decode the Refresh token
            token = RefreshToken(refresh_token)
            user_username = token["user_username"]

            # Verify the user exists and is active
            get_object_or_404(User, username=user_username, is_active=True)
        except (InvalidToken, TokenError, KeyError):
            raise AuthenticationFailed({"message": "Invalid refresh token"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "User does not exist"})

        attrs["refresh_token"] = refresh_token
        return attrs


class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")
        if not refresh_token:
            raise serializers.ValidationError({"message": "Refresh token is missing"})

        try:
            # Verify Refresh token
            token = RefreshToken(refresh_token)
            user_username = token["user_username"]

            # Verify valid user
            get_object_or_404(User, username=user_username, is_active=True)
            attrs["refresh_token"] = token
        except (InvalidToken, TokenError):
            raise AuthenticationFailed({"message": "Invalid refresh token"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "User does not exist"})

        return attrs


class UserDeleteSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")
        email = attrs.get("email")

        if not refresh_token:
            raise serializers.ValidationError({"message": "Refresh token is missing"})
        if not email:
            raise serializers.ValidationError({"message": "Email is missing"})

        try:
            # Verify Refresh token
            token = RefreshToken(refresh_token)
            user_username = token["user_username"]
            user = get_object_or_404(
                User, username=user_username, email=email, is_active=True
            )
        except (InvalidToken, TokenError) as e:
            raise AuthenticationFailed({"message": "Invalid refresh token"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "User does not exist"})

        attrs["refresh_token"] = token
        attrs["user"] = user
        return attrs
