from articles.models import Article
from rest_framework import serializers

from .models import Comment, CommentImage, CommentReaction


# 댓글 이미지 시리얼라이저
class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = ["id", "image_url"]


# 댓글 작성 및 수정 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, required=False)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "content",
            "is_selected",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_nickname",
            "is_selected",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        article_id = self.context["view"].kwargs["article_id"]
        article = Article.objects.get(id=article_id)

        # 댓글 작성자가 게시글 작성자인지 확인
        if article.user == self.context["request"].user:
            raise serializers.ValidationError(
                "게시글 작성자는 해당 게시글에 댓글을 달 수 없습니다."
            )

        images_data = validated_data.pop("images", [])
        comment = Comment.objects.create(article=article, **validated_data)
        for image_data in images_data:
            CommentImage.objects.create(comment=comment, **image_data)
        return comment


# 댓글 목록 조회 시리얼라이저
class CommentListSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "content",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_nickname",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "created_at",
            "updated_at",
        ]


# 특정 댓글 조회 시리얼라이저
class CommentDetailSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "content",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_nickname",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "created_at",
            "updated_at",
        ]


# 도움이 돼요/안돼요 시리얼 라이저
class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ["id", "user", "comment", "reaction_type", "created_at"]
        read_only_fields = ["id", "user", "comment", "created_at"]
