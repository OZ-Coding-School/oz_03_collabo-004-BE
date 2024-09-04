from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser


from ..models import Comment, CommentImage
from ..s3instance import S3Instance
from ..serializers import (
    CommentDetailSerializer,
    CommentImageSerializer,
    CommentListSerializer,
    CommentSerializer,
)


# 댓글 작성 뷰
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # 댓글 생성
        comment = serializer.save(
            user=self.request.user, article_id=self.kwargs["article_id"]
        )

        # 이미지 처리
        images = self.request.FILES.getlist("images")
        if images:
            s3instance = S3Instance().get_s3_instance()
            for image in images:
                image_url = S3Instance.upload_file(
                    s3instance, image, self.request.user.id
                )
                CommentImage.objects.create(comment=comment, image=image_url)


# 댓글 수정 뷰
class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        comment = super().get_object()

        if comment.article.is_closed:
            raise PermissionDenied("이미 마감이 된 게시글에 대하여 수정할 수 없습니다.")

        if Comment.objects.filter(article=comment.article, is_selected=True).exists():
            raise PermissionDenied(
                "이 게시글의 다른 댓글이 이미 채택되었습니다. 더 이상 댓글을 수정할 수 없습니다."
            )

        if comment.user != self.request.user:
            raise PermissionDenied("댓글을 수정할 권한이 없습니다.")

        return comment

    def perform_update(self, serializer):
        # 댓글 업데이트
        comment = serializer.save()

        # 이미지 처리 (기존 이미지 삭제 후 새로운 이미지 업로드)
        images = self.request.FILES.getlist("images")
        if images:
            s3instance = S3Instance().get_s3_instance()
            for img in comment.images.all():
                S3Instance.delete_file(s3instance, img.image)
                img.delete()
            for image in images:
                image_url = S3Instance.upload_file(
                    s3instance, image, self.request.user.id
                )
                CommentImage.objects.create(comment=comment, image=image_url)


# 댓글 목록 조회 뷰
class CommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        article_id = self.kwargs["article_id"]
        return Comment.objects.filter(article_id=article_id)


# 댓글 상세 조회 뷰
class CommentDetailView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Comment.objects.all()

    def get_object(self):
        comment = super().get_object()
        return comment



