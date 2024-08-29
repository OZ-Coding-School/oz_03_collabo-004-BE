from articles.s3instance import S3Instance
from comments.serializers import CommentListSerializer
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

    def get_user(self, obj):
        return {"user_id": obj.user.id, "nickname": obj.user.nickname}

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
    images = ArticleImageSerializer(many=True, required=False)
    tag_ids = serializers.CharField(write_only=True)
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

    def parse_tag_ids(self, tag_ids):
        if isinstance(tag_ids, str):
            # 문자열로 전달된 경우 쉼표로 구분하여 리스트로 변환
            return [
                int(tag_id.strip()) for tag_id in tag_ids.split(",") if tag_id.strip()
            ]
        elif isinstance(tag_ids, list):
            # 이미 리스트로 전달된 경우, 각 요소를 정수로 변환
            return [int(tag_id) for tag_id in tag_ids]
        return []

    def create(self, validated_data):
        tag_ids_str = validated_data.pop("tag_ids", "")
        tag_ids = self.parse_tag_ids(tag_ids_str)

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
        tag_ids_str = validated_data.pop("tag_ids", "")
        tag_ids = self.parse_tag_ids(tag_ids_str)

        # 제목과 내용을 업데이트
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.tags.set(tag_ids)
        instance.save()

        images_data = self.context["request"].FILES.getlist("images")
        images_to_delete = self.context["request"].data.get("images_to_delete", [])

        # 기존 이미지 삭제 처리
        if images_to_delete or images_data:
            s3instance = S3Instance().get_s3_instance()
            # 삭제할 이미지가 명시되었거나, 새로운 이미지가 업로드되면 모든 기존 이미지 삭제
            for image in instance.images.all():
                S3Instance.delete_file(s3instance, image.image)
                image.delete()

        # 새로운 이미지 추가
        if images_data:
            s3instance = S3Instance().get_s3_instance()
            image_urls = S3Instance.upload_files(s3instance, images_data, instance.id)

            for index, image_url in enumerate(image_urls):
                is_thumbnail = index == 0  # 첫 번째 이미지를 썸네일로 설정
                ArticleImage.objects.create(
                    article=instance, image=image_url, is_thumbnail=is_thumbnail
                )

        return instance


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
    comments = CommentListSerializer(many=True, read_only=True)  # 댓글 목록을 포함
    comments_count = serializers.IntegerField(
        source="comments.count", read_only=True
    )  # 댓글 수

    class Meta:
        model = Article
        fields = [
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
        return {"user_id": obj.user.id, "nickname": obj.user.nickname}

    def get_thumbnail_image(self, obj):
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if thumbnail_image:
            return thumbnail_image.image_url
        return None  # 썸네일 이미지가 없는경우(이미지가 아예없는 게시글)
