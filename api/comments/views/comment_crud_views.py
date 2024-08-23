from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from ..models import Comment
from ..serializers import (
    CommentDetailSerializer,
    CommentListSerializer,
    CommentSerializer,
)


# 댓글 작성 뷰
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = super().get_object()

        # 게시글이 마감되었는지 확인
        if comment.article.is_closed:
            raise PermissionDenied("이미 마감이 된 게시글에 대하여 수정할 수 없습니다.")

        # 게시글의 다른 댓글이 채택되었는지 확인
        if Comment.objects.filter(article=comment.article, is_selected=True).exists():
            raise PermissionDenied(
                "이 게시글의 다른 댓글이 이미 채택되었습니다. 더 이상 댓글을 수정할 수 없습니다."
            )

        # 댓글의 작성자인지 확인
        if comment.user != self.request.user:
            raise PermissionDenied("댓글을 수정할 권한이 없습니다.")

        return comment

    def perform_update(self, serializer):
        serializer.save()


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
