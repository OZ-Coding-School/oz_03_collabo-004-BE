from articles.models import Article
from articles.serializers import ArticleListSerializer
from comments.models import Comment
from comments.serializers import UserCommentListSerializer
from django.db.models import Count, Sum
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from tags.models import Tag
from tags.serializers import TagSerializer
from users.models import User

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    selected_tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    nickname = serializers.CharField(source="user.nickname", required=False)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    selected_comment_count = serializers.SerializerMethodField()
    hunsoo_level = serializers.IntegerField(read_only=True)
    articles = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    liked_articles_count = serializers.SerializerMethodField()
    helpful_comments_count = serializers.SerializerMethodField()
    not_helpful_comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "status",
            "user_id",
            "email",
            "bio",
            "profile_image",
            "nickname",
            "selected_tags",
            "warning_count",
            "hunsoo_level",
            "selected_comment_count",
            "liked_articles_count",
            "helpful_comments_count",
            "not_helpful_comments_count",
            "articles",
            "comments",
        ]

    def get_profile_image(self, obj):
        # URL을 직접 반환하여 올바르게 처리되도록 함
        if obj.profile_image:
            return obj.profile_image  # 혹은 obj.profile_image.url, 필요에 따라 조정
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        nickname = user_data.get("nickname")

        if nickname:
            instance.user.nickname = nickname
            instance.user.save()

        instance.bio = validated_data.get("bio", instance.bio)

        if "selected_tags" in validated_data:
            selected_tags = validated_data.pop("selected_tags")
            instance.selected_tags.set(selected_tags)

        instance.save()
        return instance

    def get_email(self, obj):
        return obj.user.email

    def get_selected_comment_count(self, obj):
        return Comment.objects.filter(user=obj.user, is_selected=True).count()

    def get_articles(self, obj):
        articles = Article.objects.filter(user=obj.user).order_by("-created_at")
        return ArticleListSerializer(articles, many=True).data

    def get_comments(self, obj):
        comments = Comment.objects.filter(user=obj.user).order_by("-created_at")
        return UserCommentListSerializer(comments, many=True).data

    def get_status(self, obj):
        return self.context.get("is_own_profile", False)

    def validate_nickname(self, value):
        user = self.context["request"].user
        if User.objects.filter(nickname=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def validate_selected_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("태그는 최대 3개까지 선택할 수 있습니다.")
        return value

    def get_liked_articles_count(self, obj):
        result = Article.objects.filter(user=obj.user).aggregate(
            total_likes=Count("likes")
        )
        return result["total_likes"] or 0

    def get_helpful_comments_count(self, obj):
        result = Comment.objects.filter(user=obj.user).aggregate(
            total_helpful=Sum("helpful_count")
        )
        return result["total_helpful"] or 0

    def get_not_helpful_comments_count(self, obj):
        result = Comment.objects.filter(user=obj.user).aggregate(
            total_not_helpful=Sum("not_helpful_count")
        )
        return result["total_not_helpful"] or 0


class AdminProfileSerializer(serializers.ModelSerializer):
    hunsoo_level = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ["hunsoo_level"]
