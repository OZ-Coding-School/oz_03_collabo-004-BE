import re

from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Article, ArticleImage
from ..s3instance import S3Instance
from ..serializers import ArticleImageSerializer, ArticleSerializer


# 게시글 작성 뷰
class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        tag_id = self.request.data.get("tag_id")
        temp_image_ids = self.request.data.get("temp_image_ids", [])
        content = self.request.data.get("content", "")

        if not tag_id:
            raise serializers.ValidationError("태그는 반드시 1개여야 합니다.")

        # 게시글 생성 및 저장 (ID는 저장 후 확정됨)
        article = serializer.save(user=self.request.user, tag_id=tag_id)

        # ID가 제대로 생성되었는지 확인
        if not article.id:
            raise serializers.ValidationError("게시글 ID가 생성되지 않았습니다.")

        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # 임시 이미지들을 게시글과 연결 및 경로 변경 (ID가 확정된 후 실행)
        S3Instance.move_temp_images_to_article(s3instance, temp_image_ids, article)

        # content에 포함된 이미지 경로 업데이트 (S3Instance 내 메서드 사용)
        s3 = S3Instance()  # S3Instance 객체 생성
        updated_content = s3.update_image_urls(content, article.id)
        article.content = updated_content
        article.save()  # 변경된 content와 함께 게시글 다시 저장

        # 직렬화된 게시글 데이터를 응답으로 반환
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
        temp_image_ids = self.request.data.get("temp_image_ids", [])
        content = self.request.data.get("content", "")

        if not tag_id:
            raise serializers.ValidationError("태그는 반드시 1개여야 합니다.")

        # 문자열로 들어온 temp_image_ids를 정수형으로 변환
        try:
            temp_image_ids = list(
                map(int, temp_image_ids)
            )  # 문자열을 정수형 리스트로 변환
        except ValueError:
            raise serializers.ValidationError("유효한 이미지 ID가 필요합니다.")

        # 게시글 수정 및 저장
        article = serializer.save(tag_id=tag_id)

        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # 기존 이미지 처리 로직
        existing_images = list(article.images.values_list("id", flat=True))

        # 새로 들어온 이미지와 기존 이미지 비교하여 삭제할 이미지 선정
        images_to_delete = set(existing_images) - set(temp_image_ids)

        # S3에서 삭제하고 DB에서도 삭제
        for image_id in images_to_delete:
            try:
                image = ArticleImage.objects.get(id=image_id)
                # S3에서 이미지 삭제
                S3Instance.delete_file(s3instance, image.image)
                # DB에서 이미지 객체 삭제
                image.delete()
            except ArticleImage.DoesNotExist:
                pass
            except Exception as e:
                raise serializers.ValidationError(
                    f"S3 이미지 삭제 중 오류가 발생했습니다: {str(e)}"
                )

        # 임시 이미지들을 게시글과 연결 및 경로 변경
        if temp_image_ids:
            S3Instance.move_temp_images_to_article(s3instance, temp_image_ids, article)

        # content에 포함된 이미지 경로 업데이트 (S3Instance 내 메서드 사용)
        s3 = S3Instance()  # S3Instance 객체 생성
        updated_content = s3.update_image_urls(content, article.id)
        article.content = updated_content
        article.save()  # 변경된 content와 함께 다시 저장

        # 수정된 게시글을 직렬화하여 응답으로 반환
        response_data = ArticleSerializer(
            article, context={"request": self.request}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)


# 이미지 업로드 뷰
class ArticleImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request):
        # 요청에서 이미지 파일 가져오기
        image_file = request.FILES.get("images")
        if not image_file:
            return Response(
                {"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # S3에 이미지 업로드 (리스트로 전달)
        image_urls = S3Instance.upload_files(s3instance, [image_file])

        # 업로드된 이미지 URL을 사용해 ArticleImage 객체 생성 및 저장
        article_image = ArticleImage.objects.create(
            image=image_urls[0],  # S3에서 반환된 URL 사용
            article=None,  # article 연결은 나중에
        )

        # 직렬화된 이미지 응답 반환 (배열 없이 단일 객체)
        image_data = ArticleImageSerializer(article_image).data
        return Response(image_data, status=status.HTTP_201_CREATED)


# 이미지 삭제 뷰
class ArticleImageDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, image_id):
        # S3 인스턴스 생성
        s3instance = S3Instance().get_s3_instance()

        # S3Instance를 통해 이미지 삭제
        try:
            # 이미지 ID에 해당하는 이미지를 S3에서 삭제하고 DB에서도 삭제
            deleted_images = S3Instance.delete_images(s3instance, [image_id])
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_200_OK)


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
