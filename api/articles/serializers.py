from django.core.files.storage import default_storage
from rest_framework import serializers
from tags.models import Tag
from tags.serializers import TagSerializer

from .models import Article, ArticleImage


# 게시글 작성시 이미지 삽입 시리얼라이저
class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ["id", "image_url", "is_thumbnail"]


# 전체 게시글조회를 위한 시리얼라이저
class ArticleListSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    thumbnail_image = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "article_id",
            "title",
            "content",
            "user",
            "tag_ids",
            "tags",
            "created_at",
            "view_count",
            "like_count",
            "thumbnail_image",
            # "hoonsu_count",
        ]

    def get_user(self, obj):
        return {"user_id": obj.user.id, "nickname": obj.user.nickname}
    
    def get_thumbnail_image(self, obj):
        thumbnail_image = obj.images.filter(is_thumbnail=True).first()
        if thumbnail_image:
            return thumbnail_image.image_url
        return None #썸네일 이미지가 없는경우(이미지가 아예없는 게시글)


# 유저의 게시글 작성과 조회를 위한 시리얼라이저
class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source="id")
    images = ArticleImageSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    user = serializers.SerializerMethodField()

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
            "created_at",
            "updated_at",
            # "hoonsu_count",
        ]

    def get_user(self, obj):
        return {"user_id": obj.user.id, "nickname": obj.user.nickname}

    def create(self, validated_data):
        tags = validated_data.pop("tag_ids", [])
        image_files = validated_data.pop("image_files", [])

        article = Article.objects.create(**validated_data)
        article.tags.add(*tags)

        for index, image_file in enumerate(image_files):
            image_url = default_storage.save(image_file.name, image_file)  # S3에 업로드
            is_thumbnail = index == 0  # 첫 번째 이미지를 썸네일로 설정
            ArticleImage.objects.create(
                article=article, image_url=image_url, is_thumbnail=is_thumbnail
            )

        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop("tag_ids", [])
        image_files = validated_data.pop("image_files", [])

        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.save()

        if tags:
            instance.tags.set(tags)

        if image_files:
            # 기존 이미지를 삭제
            instance.images.all().delete()
            # 새로운 이미지 추가
            for index, image_file in enumerate(image_files):
                image_url = default_storage.save(
                    image_file.name, image_file
                )  # S3에 업로드
                is_thumbnail = index == 0  # 첫 번째 이미지를 썸네일로 설정
                ArticleImage.objects.create(
                    article=instance, image_url=image_url, is_thumbnail=is_thumbnail
                )

        return instance
