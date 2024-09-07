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


# 게시글 작성과 수정을 위한 시리얼라이저
class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    images = ArticleImageSerializer(many=True, required=False, read_only=True)
    tag_id = serializers.IntegerField(write_only=True)
    temp_image_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
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
            "temp_image_ids",
            "images",
            "tag_id",
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
        tag_id = validated_data.pop("tag_id")
        temp_image_ids = validated_data.pop("temp_image_ids", [])
        article = Article.objects.create(**validated_data)
        article.tags.add(tag_id)

        # 임시 이미지들을 게시글에 연결하고 경로 변경
        if temp_image_ids:
            s3instance = S3Instance().get_s3_instance()
            S3Instance.move_temp_images_to_article(s3instance, temp_image_ids, article)

            # 첫 번째 임시 이미지를 썸네일로 설정
            first_image = (
                ArticleImage.objects.filter(article=article).order_by("id").first()
            )
            if first_image:
                first_image.is_thumbnail = True
                first_image.save()

        return article

    def update(self, instance, validated_data):
        tag_id = validated_data.pop("tag_id", None)
        temp_image_ids = validated_data.pop("temp_image_ids", [])

        # 제목과 내용을 업데이트
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)

        if tag_id:
            instance.tags.set([tag_id])
        instance.save()

        # 임시 이미지들을 게시글에 연결하고 경로 변경
        if temp_image_ids:
            s3instance = S3Instance().get_s3_instance()
            S3Instance.move_temp_images_to_article(s3instance, temp_image_ids, instance)

            # 기존 썸네일이 있으면 초기화
            instance.images.update(is_thumbnail=False)

            # 새로 들어온 첫 번째 이미지를 썸네일로 설정
            first_image = (
                ArticleImage.objects.filter(article=instance).order_by("id").first()
            )
            if first_image:
                first_image.is_thumbnail = True
                first_image.save()

        return instance


# 전체 게시글조회를 위한 시리얼라이저
class ArticleListSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    images = ArticleImageSerializer(many=True, required=False)
    tag_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), write_only=True
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
            "tag_id",
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
        # 썸네일 이미지가 있으면 가져오고, 없으면 첫 번째 이미지를 가져옴
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if not thumbnail_image:
            thumbnail_image = obj.images.first()
        return thumbnail_image.image_url if thumbnail_image else None

    def get_comments_count(self, obj):
        return obj.comments.count()  # 댓글 수 반환


# 게시글 상세 조회를 위한 시리얼라이저
class ArticleDetailSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    thumbnail_image = serializers.SerializerMethodField()
    images = ArticleImageSerializer(many=True, required=False)
    tag_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), write_only=True
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
            "tag_id",
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
        # 썸네일 이미지가 있으면 가져오고, 없으면 첫 번째 이미지를 가져옴
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if not thumbnail_image:
            thumbnail_image = obj.images.first()
        return thumbnail_image.image_url if thumbnail_image else None

    def get_status(self, obj):
        request = self.context.get("request")
        return request.user.is_authenticated
