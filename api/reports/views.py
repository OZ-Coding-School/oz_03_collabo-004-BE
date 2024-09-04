from articles.models import Article
from comments.models import Comment
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ArticleReport, CommentReport
from .serializers import ArticleReportSerializer, CommentReportSerializer

User = get_user_model()


class ArticleReportCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        try:
            # URL에서 전달된 article_id로 Article 객체를 조회
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            # Article 객체가 존재하지 않을 경우
            return Response(
                {"detail": "해당 게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 요청한 사용자를 reporter로 설정
        reporter = request.user

        # Article의 작성자를 reported_user로 설정
        reported_user = article.user

        # 동일한 사용자가 같은 article을 이미 신고했는지 확인
        if ArticleReport.objects.filter(
            reporter=reporter, reported_article=article
        ).exists():
            return Response(
                {"detail": "이미 신고한 게시글입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 요청 데이터에 추가 정보를 삽입하여 serializer 초기화
        data = {
            "report_detail": request.data.get("report_detail"),
            "reporter": reporter.id,
            "reported_user": reported_user.id,
            "reported_article": article.id,
        }

        serializer = ArticleReportSerializer(data=data)

        if serializer.is_valid():
            serializer.save()  # ArticleReport 모델에 데이터 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentReportCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        try:
            # URL에서 전달된 comment_id로 Comment 객체를 조회
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            # Comment 객체가 존재하지 않을 경우
            return Response(
                {"detail": "해당 댓글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 요청한 사용자를 reporter로 설정
        reporter = request.user

        # Comment의 작성자를 reported_user로 설정
        reported_user = comment.user

        # 동일한 사용자가 같은 comment를 이미 신고했는지 확인
        if CommentReport.objects.filter(
            reporter=reporter, reported_comment=comment
        ).exists():
            return Response(
                {"detail": "이미 신고한 댓글입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 요청 데이터에 추가 정보를 삽입하여 serializer 초기화
        data = {
            "report_detail": request.data.get("report_detail"),
            "reporter": reporter.id,
            "reported_user": reported_user.id,
            "reported_comment": comment.id,
        }

        serializer = CommentReportSerializer(data=data)

        if serializer.is_valid():
            serializer.save()  # CommentReport 모델에 데이터 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
