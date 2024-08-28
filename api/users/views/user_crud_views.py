from articles.models import Article
from articles.serializers import ArticleDetailSerializer
from comments.models import Comment
from comments.serializers import CommentDetailSerializer
from common.logger import logger
from django.shortcuts import get_object_or_404
from reports.models import ArticleReport, CommentReport
from reports.serializers import (
    ArticleReportAllSerializer,
    ArticleReportStatusSerializer,
    CommentReportAllSerializer,
    CommentReportStatusSerializer,
    ReportStatusSerializer,
    UserReportStatusSerializer,
)
from rest_framework import status
from rest_framework.generics import (
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import EmptySerializer, UserSerializer
from users.utils import IsAdminUser


class SwitchUserAuthorizationView(UpdateAPIView):
    serializer_class = EmptySerializer
    permission_classes = [IsAdminUser]  # 슈퍼유저만 접근 가능

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get("id")
        user = get_object_or_404(User, id=user_id)

        is_superuser = request.data.get("is_superuser")
        if is_superuser not in ["True", "False"]:
            return Response(
                {"message": "is_superuser must be 'True' or 'False'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 슈퍼유저 권한 설정
        user.is_superuser = True if is_superuser == "True" else False

        # 슈퍼유저가 되는 경우 is_staff도 True로 설정
        if user.is_superuser:
            user.is_staff = True
        else:
            # 슈퍼유저 해제 시 필요하다면 is_staff를 False로 설정 가능
            user.is_staff = False

        user.save()
        return Response(status=status.HTTP_200_OK)


# 모든 유저정보 조회
class UserListForAdmin(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 특정유저정보 조회, 수정, 삭제
class UserRetrieveUpdateDeleteAdminView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=user_id)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=user_id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User updated successfully"}, status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 특정 게시글 조회 및 삭제
class AdminArticleDetailView(RetrieveDestroyAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = Article.objects.all()
    lookup_field = "id"

    def get_object(self):
        article_id = self.kwargs.get("id")
        return get_object_or_404(Article, id=article_id)

    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 특정 댓글 조회 및 삭제
class AdminCommentDetailView(RetrieveDestroyAPIView):
    serializer_class = CommentDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = Comment.objects.all()

    def get(self, request, *args, **kwargs):
        comment_id = kwargs.get("id")
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        comment_id = kwargs.get("id")
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 특정 사용자의 게시글, 댓글 삭제
class UserArticleCommentDeleteView(DestroyAPIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("id")
        user = get_object_or_404(User, id=user_id)

        # 사용자 작성 게시글 삭제
        Article.objects.filter(user=user).delete()

        # 사용자 작성 댓글 삭제
        Comment.objects.filter(user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# 특정 게시물 신고의 신고 처리 상태 변경
class ArticleReportStatusUpdateView(UpdateAPIView):
    queryset = ArticleReport.objects.all()
    serializer_class = ArticleReportStatusSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()
        return Response(
            {"status": "Report status updated successfully"},
            status=status.HTTP_200_OK,
        )


# 특정 댓글 신고의 신고 처리 상태 변경
class CommentReportStatusUpdateView(UpdateAPIView):
    queryset = CommentReport.objects.all()
    serializer_class = CommentReportStatusSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()
        return Response(
            {"status": "Report status updated successfully"},
            status=status.HTTP_200_OK,
        )


# 특정 유저 신고 내역 확인
class UserReportStatusView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserReportStatusSerializer

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")

        # 특정 유저에 대한 신고 내역 조회
        article_reports = ArticleReport.objects.filter(reported_user_id=user_id)
        comment_reports = CommentReport.objects.filter(reported_user_id=user_id)

        # 직렬화
        serializer = self.get_serializer(
            {"article_reports": article_reports, "comment_reports": comment_reports}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


# 신고 내역 전체 확인
class ReportListView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ReportStatusSerializer

    def get(self, request, *args, **kwargs):
        article_reports = ArticleReport.objects.all()
        comment_reports = CommentReport.objects.all()

        # 직렬화
        serializer = self.get_serializer(
            {"article_reports": article_reports, "comment_reports": comment_reports}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
