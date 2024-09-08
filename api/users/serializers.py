from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from profiles.models import Profile
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from tags.models import Tag
from users.models import User


class EmptySerializer(serializers.Serializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "nickname"]
        extra_kwargs = {
            "email": {"validators": []},
            "username": {"validators": []},
            "nickname": {"validators": []},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            user = User.objects.get(email=value)
            if user.social_platform != "general":
                raise serializers.ValidationError(
                    detail={
                        "message": "구글 계정으로 이미 가입된 사용자입니다.",
                        "code": "01",
                    }
                )
            raise serializers.ValidationError(
                detail={
                    "message": "일반 회원으로 이미 가입된 사용자입니다.",
                    "code": "02",
                }
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data["nickname"],
            is_staff=False,
        )
        user.social_platform = "general"
        user.is_email_verified = False
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError("아이디와 비밀번호가 필요합니다.")
        # 사용자 인증 확인
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("잘못된 아이디 또는 비밀번호입니다.")

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


class UserSerializer(serializers.ModelSerializer):
    selected_tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, source="profile.selected_tags"
    )
    hunsoo_level = serializers.IntegerField(source="profile.hunsoo_level")
    warning_count = serializers.IntegerField(source="profile.warning_count")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "email",
            "social_platform",
            "is_superuser",
            "is_active",
            "last_login",
            "created_at",
            "updated_at",
            "hunsoo_level",
            "warning_count",
            "selected_tags",
        ]
