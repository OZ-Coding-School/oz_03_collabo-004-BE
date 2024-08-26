from articles.models import Article
from django.contrib.auth import get_user_model
from django.urls import reverse
from reports.models import ArticleReport
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class ArticleReportCreateViewTest(APITestCase):
    def setUp(self):

        # APIClient 초기화
        self.client = APIClient()

        # 테스트용 사용자 생성
        self.reporter = User.objects.create_user(
            email="reporter@example.com",
            username="reporter",
            password="reporterpassword",
            nickname="reporter",
            social_platform="general",
        )

        # 신고당할 게시글 작성자 생성
        self.reported_user = User.objects.create_user(
            email="reported@example.com",
            username="reported",
            password="reportedpassword",
            nickname="reported",
            social_platform="general",
        )

        # 게시글 생성
        self.article = Article.objects.create(
            user=self.reported_user,
            title="Test Article",
            content="This is a test article.",
            is_closed=False,
            view_count=0,
        )

        # API 엔드포인트 URL 설정
        self.url = reverse(
            "article-report-create", kwargs={"article_id": self.article.id}
        )

    def test_report_article_success(self):
        # 올바른 데이터로 POST 요청
        data = {
            "report_detail": "spam or inappropriate content",
        }
        self.client.force_authenticate(user=self.reporter)
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArticleReport.objects.count(), 1)
        self.assertEqual(
            ArticleReport.objects.get().report_detail, "spam or inappropriate content"
        )
        self.assertEqual(ArticleReport.objects.get().reported_article, self.article)
        self.assertEqual(ArticleReport.objects.get().reporter, self.reporter)
        self.assertEqual(ArticleReport.objects.get().reported_user, self.reported_user)

    def test_report_article_failure_missing_field(self):
        # 누락된 필드로 POST 요청
        data = {}
        self.client.force_authenticate(user=self.reporter)
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("report_detail", response.data)

    def test_report_article_not_found(self):
        # 존재하지 않는 게시글에 대한 신고 시도
        url = reverse("article-report-create", kwargs={"article_id": 9999})
        data = {
            "report_detail": "spam or inappropriate content",
        }
        self.client.force_authenticate(user=self.reporter)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "해당 게시글을 찾을 수 없습니다.")

    def test_unauthenticated_user(self):
        # 인증되지 않은 사용자로 POST 요청
        data = {
            "report_detail": "spam or inappropriate content",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
