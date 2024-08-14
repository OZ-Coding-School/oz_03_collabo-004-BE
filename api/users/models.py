import uuid

from common.models import TimeStampedModel
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username=None,
        password=None,
        nickname=None,
        social_platform="general",
        **extra_fields
    ):
        if not email:
            raise ValueError("이메일 정보를 가져올 수 없습니다")

        if social_platform == "general":  # 일반 로그인인 경우
            if not username or not password or not nickname:
                raise ValueError(
                    "일반 로그인에는 username(id), password, nickname이 필요합니다"
                )
        else:  # 소셜 로그인인 경우
            if not username:
                username = str(uuid.uuid4())  # username을 uuid로 설정
            password = None  # password는 None으로 설정 (set_unusable_password에서 처리)

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            nickname=nickname,  # nickname 추가
            social_platform=social_platform,
            **extra_fields
        )

        if social_platform == "general":
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("social_platform", "general")

        if not email:
            raise ValueError("이메일 정보를 가져올 수 없습니다")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(TimeStampedModel, AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True, null=False)
    email = models.EmailField(unique=True, null=False)
    nickname = models.CharField(max_length=255, null=False)
    social_platform = models.CharField(
        choices=[("general", "general"), ("google", "google")],
        max_length=50,
        null=False,
        default="none",
    )
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
