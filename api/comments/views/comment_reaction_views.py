from ai_hunsoos.models import AiHunsoo
from ai_hunsoos.serializers import AiHunsooSerializer
from django.db import transaction
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
        with transaction.atomic():
            # 댓글 채택 로직
            comment = self.get_object()

            # 게시글이 이미 마감되었는지 확인
            if comment.article.is_closed:
                raise PermissionDenied("이미 마감된 게시글입니다.")

            # 이미 다른 댓글이 채택되었는지 확인
            if Comment.objects.filter(
                article=comment.article, is_selected=True
            ).exists():
                raise PermissionDenied("이미 다른 댓글이 채택되었습니다.")

            # 댓글을 채택하고 게시글을 마감
            comment.is_selected = True
            comment.article.is_closed = True
            comment.save()
            comment.article.save()

            # 댓글이 속한 게시글과 연결된 AiHunsoo 인스턴스를 가져오기
            try:
                ai_hunsoo = AiHunsoo.objects.get(article=comment.article)
                ai_hunsoo_data = AiHunsooSerializer(ai_hunsoo).data
            except AiHunsoo.DoesNotExist:
                ai_hunsoo_data = None

            return ai_hunsoo_data

    def update(self, request, *args, **kwargs):
        # perform_update 메서드에서 원하는 데이터를 반환받음
        ai_hunsoo_data = self.perform_update(self.get_serializer())
        return Response(ai_hunsoo_data)


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

        # 댓글 작성자가 자신의 댓글에 반응하지 못하도록 함
        if comment.user == user:
            return Response(
                {"detail": "You cannot react to your own comment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


# helpful 기반으로한 상위 5개의 댓글 반환
class TopHelpfulCommentsView(APIView):
    """
    helpful_count 기준 상위 5개의 댓글을 반환하는 API
    """

    def get(self, request, *args, **kwargs):
        # helpful_count 필드 기준으로 내림차순 정렬하여 상위 5개의 댓글을 가져옴
        top_comments = Comment.objects.order_by("-helpful_count")[:5]
        # 시리얼라이저로 직렬화
        serializer = CommentSerializer(top_comments, many=True)
        # 응답 반환
        return Response(serializer.data, status=status.HTTP_200_OK)
