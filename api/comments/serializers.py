from articles.models import Article
from rest_framework import serializers
from tags.serializers import TagSerializer

from .models import Comment, CommentImage, CommentReaction


# 댓글 이미지 시리얼라이저
class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = ["id", "image"]


# 댓글 작성 및 수정 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, required=False)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "user_profile_image",
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
            "user_profile_image",
            "is_selected",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        article_id = self.context["view"].kwargs["article_id"]
        article = Article.objects.get(id=article_id)

        # 댓글 작성자가 게시글 작성자인지 확인
        if article.user == self.context["request"].user:
            raise serializers.ValidationError(
                "게시글 작성자는 해당 게시글에 댓글을 달 수 없습니다."
            )

        # 동일한 사용자가 동일한 게시글에 댓글을 다시 작성하려는지 확인

        if Comment.objects.filter(
            user=self.context["request"].user, article=article
        ).exists():
            raise serializers.ValidationError(
                "해당 게시글에 이미 댓글을 작성하셨습니다."
            )

        # 이미지는 뷰에서 처리되므로 시리얼라이저에서는 생성된 댓글만 반환
        comment = Comment.objects.create(article=article, **validated_data)
        return comment

    def update(self, instance, validated_data):
        # 이미지는 뷰에서 처리되므로 시리얼라이저에서는 댓글만 업데이트
        return super().update(instance, validated_data)

    def get_user_profile_image(self, obj):
        profile = obj.user.profile
        if profile:
            return profile.profile_image
        return None


# 댓글 목록 조회 시리얼라이저
class CommentListSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)
    user_profile_image = serializers.SerializerMethodField()
    user_hunsoo_level = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "user_profile_image",
            "user_hunsoo_level",
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
            "user_profile_image",
            "user_hunsoo_level",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "created_at",
            "updated_at",
        ]

    def get_user_profile_image(self, obj):
        profile = obj.user.profile
        if profile and profile.profile_image:
            return profile.profile_image
        return None

    def get_user_hunsoo_level(self, obj):
        profile = obj.user.profile
        if profile:
            return profile.hunsoo_level
        return None


# 게시글 조회 시 필요한 댓글 목록 조회 시리얼라이저
class CommentArticleListSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)
    user_profile_image = serializers.SerializerMethodField()
    user_hunsoo_level = serializers.SerializerMethodField()
    reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "user_profile_image",
            "user_hunsoo_level",
            "content",
            "is_selected",
            "reaction",
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
            "user_profile_image",
            "user_hunsoo_level",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "created_at",
            "updated_at",
        ]

    def get_user_profile_image(self, obj):
        profile = obj.user.profile
        if profile:
            return profile.profile_image
        return None

    def get_user_hunsoo_level(self, obj):
        profile = obj.user.profile
        if profile:
            return profile.hunsoo_level
        return None

    def get_reaction(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            user_reaction = CommentReaction.objects.filter(
                user=request.user, comment=obj
            ).first()
            if user_reaction:
                return user_reaction.reaction_type
        return "none"


class UserCommentListSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)

    # 댓글이 달린 게시글의 추가 정보
    article_title = serializers.CharField(source="article.title", read_only=True)
    article_id = serializers.CharField(source="article.id", read_only=True)
    article_user_id = serializers.IntegerField(source="article.user.id", read_only=True)
    article_user_nickname = serializers.CharField(
        source="article.user.nickname", read_only=True
    )
    article_tags = TagSerializer(source="article.tags", many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "user_profile_image",
            "content",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "images",
            "article_id",
            "article_title",
            "article_user_id",
            "article_user_nickname",
            "article_tags",
            "created_at",
            "updated_at",
        ]
        ordering = ["created_at"]


# 특정 댓글 조회 시리얼라이저
class CommentDetailSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)
    user_profile_image = serializers.SerializerMethodField()
    user_hunsoo_level = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_nickname",
            "user_profile_image",
            "user_hunsoo_level",
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
            "user_profile_image",
            "user_hunsoo_level",
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "created_at",
            "updated_at",
        ]

    def get_user_profile_image(self, obj):
        profile = obj.user.profile
        if profile and profile.profile_image:
            return profile.profile_image
        return None

    def get_user_hunsoo_level(self, obj):
        profile = obj.user.profile
        if profile:
            return profile.hunsoo_level
        return None


# 도움이 돼요/안돼요 시리얼 라이저
class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ["id", "user", "comment", "reaction_type", "created_at"]
        read_only_fields = ["id", "user", "comment", "created_at"]
