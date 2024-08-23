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

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "article",
            "content",
            "is_selected",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "article",
            "is_selected",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        comment = Comment.objects.create(**validated_data)
        for image_data in images_data:
            CommentImage.objects.create(comment=comment, **image_data)
        return comment

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])
        instance.content = validated_data.get("content", instance.content)
        instance.save()

        # 이미지 업데이트
        instance.images.all().delete()  # 기존 이미지를 삭제하고
        for image_data in images_data:
            CommentImage.objects.create(comment=instance, **image_data)

        return instance


# 댓글 목록 조회 시리얼라이저
class CommentListSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()  # 유저를 문자열로 표현
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
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
            "is_selected",
            "helpful_count",
            "not_helpful_count",
            "created_at",
            "updated_at",
        ]


# 특정 댓글 조회 시리얼라이저
class CommentDetailSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()  # 유저를 문자열로 표현
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
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
