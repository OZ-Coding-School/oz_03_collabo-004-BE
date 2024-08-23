"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
# SECRET_KEY = "django-insecure-)$!7mkpry9&^j3o!l#3-fi&v&y-^x2om_6*^^gc(%a2mii91i5"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOWED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS if origin]


CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True  # 쿠키 등 credential 정보 허용
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ai_hunsoos.apps.AiHunsoosConfig",
    "articles.apps.ArticlesConfig",
    "comments.apps.CommentsConfig",
    "common.apps.CommonConfig",
    "profiles.apps.ProfilesConfig",
    "reports.apps.ReportsConfig",
    "tags.apps.TagsConfig",
    "users.apps.UsersConfig",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "common.authentication.cookie_authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),  # 액세스 토큰 만료 시간
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),  # 리프레시 토큰 만료 시간
    "ROTATE_REFRESH_TOKENS": False,  # 리프레시 토큰 순환 사용 여부
    "BLACKLIST_AFTER_ROTATION": False,  # 순환 사용 시 이전 리프레시 토큰 블랙리스트 등록 여부
    "AUTH_HEADER_TYPES": ("Bearer",),  # 인증 헤더 타입
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",  # JWT 서명에 “HS256” 알고리즘을 사용
    "AUTH_TOKEN_CLASSES": (
        "rest_framework_simplejwt.tokens.AccessToken",
    ),  # 기본적으로 AccessToken 클래스를 사용
    "TOKEN_TYPE_CLAIM": "token_type",  # JWT에서 토큰 유형을 token_type 클레임으로 저장
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "users.User"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("RDS_HOSTNAME"),
        "NAME": os.environ.get("RDS_DB_NAME"),
        "USER": os.environ.get("RDS_USERNAME"),
        "PASSWORD": os.environ.get("RDS_PASSWORD"),
        "PORT": os.environ.get("RDS_DB_PORT", 5432),
        "OPTIONS": {
            "client_encoding": "UTF8",  # UTF-8 문자셋 설정
        },
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# AWS S3 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# 배포에서 다음 url사용
# AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")

# 미디어 파일 저장 설정
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
