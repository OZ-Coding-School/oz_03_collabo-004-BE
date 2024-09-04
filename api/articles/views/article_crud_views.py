from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Article, ArticleImage
from ..s3instance import S3Instance
from ..serializers import ArticleImageSerializer, ArticleSerializer


# 게시글 작성
class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        tag_id = self.request.data.get("tag_id")

        # 태그가 1개 이상일 수 없으므로 검증 로직은 불필요
        if not tag_id:
            raise serializers.ValidationError("태그는 반드시 1개여야 합니다.")

        article = serializer.save(user=self.request.user, tag_id=tag_id)

        # 생성된 객체를 직렬화하여 응답으로 반환
        response_data = ArticleSerializer(
            article, context={"request": self.request}
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)


# 게시글 수정
class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        article = super().get_object()
        if article.is_closed:
            raise PermissionDenied("채택이 이루어진 게시글은 수정할 수 없습니다.")
        if article.user != self.request.user:
            raise PermissionDenied("게시글 수정권한이 없는 유저입니다.")
        return article

    def perform_update(self, serializer):
        tag_id = self.request.data.get("tag_id")

        if not tag_id:
            raise serializers.ValidationError("태그는 반드시 1개여야 합니다.")

        article = serializer.save(tag_id=tag_id)

        response_data = ArticleSerializer(
            article, context={"request": self.request}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)


# 게시글 이미지 생성, 수정
class ArticleImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, id):
        article = Article.objects.get(id=id)

        # 권한 확인
        if article.user != request.user:
            return Response(
                {"message": "이미지 업로드 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        images_data = request.FILES.getlist("images")
        if images_data:
            s3instance = S3Instance().get_s3_instance()

            # 기존 이미지 삭제 (필요한 경우)
            for image in article.images.all():
                S3Instance.delete_file(s3instance, image.image)
                image.delete()

            # 새로운 이미지 업로드
            uploaded_images = []
            image_urls = S3Instance.upload_files(s3instance, images_data, article.id)

            for index, image_url in enumerate(image_urls):
                is_thumbnail = index == 0  # 첫 번째 이미지를 썸네일로 설정
                article_image = ArticleImage.objects.create(
                    article=article, image=image_url, is_thumbnail=is_thumbnail
                )
                uploaded_images.append(article_image)

            # 업로드된 이미지 정보를 직렬화하여 반환
            serialized_images = ArticleImageSerializer(uploaded_images, many=True)
            return Response(serialized_images.data, status=status.HTTP_200_OK)

        return Response(
            {"message": "업로드된 이미지가 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
