from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Comment, CommentReaction
from ..serializers import CommentSerializer


# 댓글 채택 뷰
class CommentSelectView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = super().get_object()
        # 댓글이 속한 게시글의 작성자만 댓글을 채택할 수 있도록 제한
        if comment.article.user != self.request.user:
            raise PermissionDenied("이 댓글을 채택할 권한이 없습니다.")
        return comment

    def perform_update(self, serializer):
        # 댓글 채택 로직
        comment = self.get_object()

        # 게시글이 이미 마감되었는지 확인
        if comment.article.is_closed:
            raise PermissionDenied("이미 마감된 게시글입니다.")

        # 이미 다른 댓글이 채택되었는지 확인
        if Comment.objects.filter(article=comment.article, is_selected=True).exists():
            raise PermissionDenied("이미 다른 댓글이 채택되었습니다.")

        # 댓글을 채택하고 게시글을 마감
        comment.is_selected = True
        comment.article.is_closed = True
        comment.save()
        comment.article.save()

        serializer.instance = comment
        return Response(
            {
                "message": "댓글이 채택되었고, 게시글이 마감되었습니다.",
                "data": serializer.data,
            }
        )


class CommentReactionToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get("pk")
        comment = get_object_or_404(Comment, id=comment_id)
        reaction_type = request.data.get(
            "reaction_type"
        )  # 'helpful' 또는 'not_helpful'

        if reaction_type not in ["helpful", "not_helpful"]:
            return Response(
                {"detail": "Invalid reaction type."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        reaction, created = CommentReaction.objects.get_or_create(
            user=user, comment=comment
        )

        if not created and reaction.reaction_type == reaction_type:
            # 기존 반응과 동일한 반응을 다시 누르면 삭제
            reaction.delete()
            if reaction_type == "helpful":
                comment.helpful_count -= 1
            else:
                comment.not_helpful_count -= 1
            comment.save()
            return Response(
                {"detail": f"{reaction_type} reaction removed."},
                status=status.HTTP_200_OK,
            )
        else:
            # 새로운 반응을 추가하거나 기존 반응을 변경
            if not created:
                if reaction.reaction_type == "helpful":
                    comment.helpful_count -= 1
                else:
                    comment.not_helpful_count -= 1

            reaction.reaction_type = reaction_type
            reaction.save()

            if reaction_type == "helpful":
                comment.helpful_count += 1
            else:
                comment.not_helpful_count += 1

            comment.save()

            if created:
                return Response(
                    {"detail": f"{reaction_type} reaction added."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"detail": f"Reaction changed to {reaction_type}."},
                    status=status.HTTP_200_OK,
                )
