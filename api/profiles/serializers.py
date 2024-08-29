import uuid

import boto3
from articles.models import Article
from articles.serializers import ArticleListSerializer
from comments.models import Comment
from comments.serializers import CommentListSerializer
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from tags.models import Tag
from tags.serializers import TagSerializer
from users.models import User

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    selected_tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    nickname = serializers.CharField(source="user.nickname", required=False)
    selected_comment_count = serializers.SerializerMethodField()
    hunsoo_level = serializers.IntegerField(read_only=True)
    articles = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    profile_image = serializers.ImageField()

    class Meta:
        model = Profile
        fields = [
            "status",
            "bio",
            "profile_image",
            "nickname",
            "selected_tags",
            "warning_count",
            "hunsoo_level",
            "selected_comment_count",
            "articles",
            "comments",
        ]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(ProfileSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_selected_comment_count(self, obj):
        return Comment.objects.filter(user=obj.user, is_selected=True).count()

    def get_articles(self, obj):
        articles = Article.objects.filter(user=obj.user)
        return ArticleListSerializer(articles, many=True).data

    def get_comments(self, obj):
        comments = Comment.objects.filter(user=obj.user)
        return CommentListSerializer(comments, many=True).data

    def get_status(self, obj):
        # `is_own_profile`이 컨텍스트에 있는지 확인하고, 없으면 기본값으로 False 설정
        return self.context.get("is_own_profile", False)

    def validate_hunsoo_level(self, value):
        if value < 1 or value > 100:  # 훈수 레벨의 범위를 1에서 100으로 제한
            raise serializers.ValidationError("Invalid hunsoo level")
        return value

    def validate_nickname(self, value):
        user = self.context["request"].user
        if User.objects.filter(nickname=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        nickname = user_data.get("nickname")

        if nickname:
            instance.user.nickname = nickname
            instance.user.save()

        instance.bio = validated_data.get("bio", instance.bio)
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image
        )

        selected_tags = validated_data.pop("selected_tags", None)
        if selected_tags:
            instance.selected_tags.set(selected_tags)

        return super().update(instance, validated_data)


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["profile_image"]

    def update(self, instance, validated_data):
        # 기존 이미지 삭제 (선택적)
        if (
            "profile_image" in validated_data
            and instance.profile_image
            and validated_data["profile_image"] != instance.profile_image
        ):
            instance.profile_image.delete()

        # 업데이트된 데이터 저장
        return super().update(instance, validated_data)

    def validate_profile_image(self, value):
        # S3 업로드 로직
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # 파일 확장자 검사 (선택적)
        allowed_extensions = ["jpg", "jpeg", "png"]
        extension = value.name.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError("허용된 파일 형식이 아닙니다.")

        # S3에 업로드
        key = f"profile_images/{uuid.uuid4()}.{extension}"
        s3.upload_fileobj(value, settings.AWS_STORAGE_BUCKET_NAME, key)

        # 업로드된 파일의 URL 반환
        return f"/{key}"
