from articles.models import Article
from articles.serializers import ArticleListSerializer
from comments.models import Comment
from comments.serializers import CommentListSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from tags.models import Tag
from tags.serializers import TagSerializer

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

    class Meta:
        model = Profile
        fields = [
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

    def validate_hunsoo_level(self, value):
        if value < 1 or value > 20:  # 훈수 레벨의 범위를 1에서 20으로 제한
            raise serializers.ValidationError("Invalid hunsoo level")
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
