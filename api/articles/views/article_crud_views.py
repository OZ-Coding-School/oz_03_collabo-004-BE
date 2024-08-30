from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Article, ArticleImage
from ..s3instance import S3Instance
from ..serializers import ArticleImageSerializer, ArticleSerializer


# 게시글 작성
class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # tag_ids가 이미 리스트로 전달되면 이를 처리
        tag_ids = self.request.data.get("tag_ids", "")
        if isinstance(tag_ids, str):
            tag_ids = [
                int(tag_id.strip()) for tag_id in tag_ids.split(",") if tag_id.strip()
            ]

        if len(tag_ids) > 3:
            raise serializers.ValidationError("태그는 최대 3개까지만 가능합니다.")

        article = serializer.save(user=self.request.user, tag_ids=tag_ids)

        # 생성된 객체를 직렬화하여 응답으로 반환
        return Response(
            ArticleSerializer(article, context={"request": self.request}).data,
            status=status.HTTP_201_CREATED,
        )


# 게시글 수정
class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "id"

    def get_object(self):
        article = super().get_object()
        if article.is_closed:
            raise PermissionDenied("채택이 이루어진 게시글은 수정할 수 없습니다.")
        if article.user != self.request.user:
            raise PermissionDenied("게시글 수정권한이 없는 유저입니다.")
        return article

    def perform_update(self, serializer):
        article = serializer.save()

        images_data = self.request.FILES.getlist("images")
        if images_data:
            s3instance = S3Instance().get_s3_instance()
            # 기존 이미지 삭제
            for image in article.images.all():
                S3Instance.delete_file(s3instance, image.image)
                image.delete()

            # 새로운 이미지 업로드
            image_urls = S3Instance.upload_files(s3instance, images_data, article.id)
            for index, image_url in enumerate(image_urls):
                is_thumbnail = index == 0  # 첫 번째 이미지를 썸네일로 설정
                ArticleImage.objects.create(
                    article=article, image=image_url, is_thumbnail=is_thumbnail
                )

        return article


# 게시글 삭제
class ArticleDeleteView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("본인의 게시글만 삭제할 수 있습니다.")
        if instance.is_closed:
            raise PermissionDenied("채택이 이루어진 게시글은 삭제할 수 없습니다.")
        super().perform_destroy(instance)
