from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Article, ArticleImage
from ..s3instance import S3Instance
from ..serializers import ArticleImageSerializer, ArticleSerializer


# 게시글 작성 뷰
class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        tag_id = self.request.data.get("tag_id")
        temp_image_ids = self.request.data.get("temp_image_ids", [])  # 리스트로 받음

        if not tag_id:
            raise serializers.ValidationError("태그는 반드시 1개여야 합니다.")

        # 게시글 생성
        article = serializer.save(user=self.request.user, tag_id=tag_id)

        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # 임시 이미지들을 게시글과 연결 및 경로 변경
        # temp_image_ids는 이미 리스트이므로, split() 필요 없음
        S3Instance.move_temp_images_to_article(s3instance, temp_image_ids, article)

        # 생성된 게시글을 직렬화하여 응답으로 반환
        response_data = ArticleSerializer(
            article, context={"request": self.request}
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)


# 게시글 수정 뷰
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
            raise PermissionDenied("게시글 수정 권한이 없습니다.")
        return article

    def perform_update(self, serializer):
        tag_id = self.request.data.get("tag_id")
        temp_image_ids_str = self.request.data.get("temp_image_ids", "")

        if not tag_id:
            raise serializers.ValidationError("태그는 반드시 1개여야 합니다.")

        # 게시글 수정
        article = serializer.save(tag_id=tag_id)

        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # 임시 이미지들을 게시글과 연결 및 경로 변경
        temp_image_ids = (
            list(map(int, temp_image_ids_str.split(","))) if temp_image_ids_str else []
        )
        S3Instance.move_temp_images_to_article(s3instance, temp_image_ids, article)

        # 수정된 게시글을 직렬화하여 응답으로 반환
        response_data = ArticleSerializer(
            article, context={"request": self.request}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)


# 이미지 업로드 뷰
class ArticleImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        images_data = request.FILES.getlist("images")
        if not images_data:
            return Response(
                {"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        s3instance = S3Instance().get_s3_instance()
        uploaded_images = []
        image_urls = S3Instance.upload_files(s3instance, images_data, "temporary")

        for image_url in image_urls:
            # 이미지 객체를 임시로 생성 (게시글과 연결되지 않음)
            image_instance = ArticleImage.objects.create(
                image=image_url, is_temporary=True
            )
            uploaded_images.append(image_instance)

        # 업로드된 이미지의 임시 ID를 반환
        serialized_images = ArticleImageSerializer(uploaded_images, many=True)
        temp_image_ids = [image.id for image in uploaded_images]

        return Response(
            {"temp_image_ids": temp_image_ids, "images": serialized_images.data},
            status=status.HTTP_201_CREATED,
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

        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # 게시글에 연결된 이미지들을 삭제
        for image in instance.images.all():
            S3Instance.delete_file(s3instance, image.image)  # S3에서 이미지 삭제
            image.delete()  # DB에서 이미지 객체 삭제

        super().perform_destroy(instance)
