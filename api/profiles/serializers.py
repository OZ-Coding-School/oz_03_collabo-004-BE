from articles.models import Article
from articles.serializers import ArticleListSerializer
from comments.models import Comment
from comments.serializers import CommentListSerializer
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
    email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "status",
            "email",
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

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        nickname = user_data.get("nickname")

        if nickname:
            instance.user.nickname = nickname
            instance.user.save()

        instance.bio = validated_data.get("bio", instance.bio)
        selected_tags = validated_data.pop("selected_tags", None)
        if selected_tags:
            instance.selected_tags.set(selected_tags)

        instance.save()
        return instance

    def get_email(self, obj):
        return obj.user.email

    def get_selected_comment_count(self, obj):
        return Comment.objects.filter(user=obj.user, is_selected=True).count()

    def get_articles(self, obj):
        articles = Article.objects.filter(user=obj.user)
        return ArticleListSerializer(articles, many=True).data

    def get_comments(self, obj):
        comments = Comment.objects.filter(user=obj.user)
        return CommentListSerializer(comments, many=True).data

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


class AdminProfileSerializer(serializers.ModelSerializer):
    hunsoo_level = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ["hunsoo_level"]
