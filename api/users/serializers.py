from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class EmptySerializer(serializers.Serializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "nickname"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            user = User.objects.get(email=value)
            if user.social_platform != "general":
                raise serializers.ValidationError(
                    "구글계정으로 이미 가입된 사용자 입니다."
                )
            raise serializers.ValidationError("일반회원으로 이미 가입된 사용자 입니다.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data["nickname"],
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError("아이디와 비밀번호가 필요합니다.")

        return data


class UserTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")
        if not refresh_token:
            raise serializers.ValidationError({"message": "Refresh token is missing"})

        try:
            # Verify and decode the Refresh token
            token = RefreshToken(refresh_token)
            user_id = token["user_id"]

            # Verify the user exists and is active
            get_object_or_404(User, id=user_id, is_active=True)
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
            user_id = token["user_id"]

            # Verify valid user
            get_object_or_404(User, id=user_id, is_active=True)
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
            user_id = token["user_id"]
            user = get_object_or_404(User, id=user_id, email=email, is_active=True)
        except (InvalidToken, TokenError) as e:
            raise AuthenticationFailed({"message": "Invalid refresh token"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "User does not exist"})

        attrs["refresh_token"] = token
        attrs["user"] = user
        return attrs
