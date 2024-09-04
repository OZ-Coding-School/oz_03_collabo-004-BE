from articles.s3instance import S3Instance
from comments.serializers import CommentArticleListSerializer, CommentListSerializer
from django.core.files.storage import default_storage
from rest_framework import serializers
from tags.models import Tag
from tags.serializers import TagSerializer

from .models import Article, ArticleImage


# 게시글 작성시 이미지 삽입 시리얼라이저
class ArticleImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ArticleImage
        fields = ["id", "image_url", "is_thumbnail"]

    def get_image_url(self, obj):
        # S3에 저장된 이미지의 URL 반환
        if obj.image:
            return obj.image  # image는 S3 URL을 직접 저장한 필드
        return None

# 전체 게시글조회를 위한 시리얼라이저
class ArticleListSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    images = ArticleImageSerializer(many=True, required=False)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    thumbnail_image = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    # annotate_liked_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "article_id",
            "title",
            "content",
            "images",
            "user",
            "tag_ids",
            "tags",
            "view_count",
            "like_count",
            # "annotate_liked_count",
            "comments_count",
            "created_at",
            "updated_at",
            "thumbnail_image",
        ]

    def get_user(self, obj):
        user = obj.user
        profile = user.profile
        return {
            "user_id": obj.user.id,
            "nickname": obj.user.nickname,
            "profile_image": profile.profile_image,
            "hunsoo_level": profile.hunsoo_level,
        }

    def get_thumbnail_image(self, obj):
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if thumbnail_image:
            return thumbnail_image.image_url
        return None  # 썸네일 이미지가 없는경우(이미지가 아예없는 게시글)

    def get_comments_count(self, obj):
        return obj.comments.count()  # 댓글 수 반환


# 유저의 게시글 작성과 수정을 위한 시리얼라이저
class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    images = ArticleImageSerializer(many=True, required=False, read_only=True)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "article_id",
            "user",
            "title",
            "content",
            "images",
            "tag_ids",
            "tags",
            "is_closed",
            "view_count",
            "like_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]

    def get_user(self, obj):
        return {"user_id": obj.user.id, "nickname": obj.user.nickname}

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])

        article = Article.objects.create(**validated_data)
        article.tags.add(*tag_ids)

        images_data = self.context["request"].FILES.getlist("images")
        if images_data:
            s3instance = S3Instance().get_s3_instance()
            image_urls = S3Instance.upload_files(s3instance, images_data, article.id)

            for index, image_url in enumerate(image_urls):
                is_thumbnail = index == 0  # 첫 번째 이미지를 썸네일로 설정
                ArticleImage.objects.create(
                    article=article, image=image_url, is_thumbnail=is_thumbnail
                )

        return article

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])  # 배열로 받은 tag_ids

        # 제목과 내용을 업데이트
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.tags.set(tag_ids)
        instance.save()

        return instance


# 전체 게시글조회를 위한 시리얼라이저
class ArticleListSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    images = ArticleImageSerializer(many=True, required=False)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    thumbnail_image = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "article_id",
            "title",
            "content",
            "images",
            "user",
            "tag_ids",
            "tags",
            "view_count",
            "like_count",
            "comments_count",
            "created_at",
            "updated_at",
            "thumbnail_image",
        ]
        ordering = ["created_at"]

    def get_user(self, obj):
        user = obj.user
        profile = user.profile
        return {
            "user_id": obj.user.id,
            "nickname": obj.user.nickname,
            "profile_image": profile.profile_image,
            "hunsoo_level": profile.hunsoo_level,
        }

    def get_thumbnail_image(self, obj):
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if thumbnail_image:
            return thumbnail_image.image_url
        return None  # 썸네일 이미지가 없는경우(이미지가 아예없는 게시글)

    def get_comments_count(self, obj):
        return obj.comments.count()  # 댓글 수 반환


# 게시글 상세 조회를 위한 시리얼라이저
class ArticleDetailSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    thumbnail_image = serializers.SerializerMethodField()
    images = ArticleImageSerializer(many=True, required=False)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    comments = CommentArticleListSerializer(
        many=True, read_only=True
    )  # 댓글 목록을 포함
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    # 댓글 수
    status = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "status",
            "article_id",
            "user",
            "thumbnail_image",
            "title",
            "content",
            "images",
            "tag_ids",
            "tags",
            "is_closed",
            "view_count",
            "like_count",
            "comments_count",
            "created_at",
            "updated_at",
            "comments",
        ]

    def get_user(self, obj):
        user = obj.user
        profile = user.profile
        return {
            "user_id": obj.user.id,
            "nickname": obj.user.nickname,
            "profile_image": profile.profile_image,
            "hunsoo_level": profile.hunsoo_level,
        }

    def get_thumbnail_image(self, obj):
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if thumbnail_image:
            return thumbnail_image.image_url
        return None  # 썸네일 이미지가 없는경우(이미지가 아예없는 게시글)

    def get_status(self, obj):
        request = self.context.get("request")
        return request.user.is_authenticated
