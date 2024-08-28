from articles.models import Article
from comments.models import Comment
from django.urls import reverse
from profiles.models import Profile
from reports.models import ArticleReport, CommentReport
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class AdminUserTests(APITestCase):

    def setUp(self):
        # 어드민 유저 생성
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            nickname="adminnickname",
        )
        self.access_token = self.get_access_token(self.admin_user)

        # 일반 유저 생성
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="userpassword",
            nickname="testnickname",
        )
        self.profile = Profile.objects.create(user=self.user, hunsoo_level=1)

        # 일반 유저2 생성
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="userpassword2",
            nickname="testnickname2",
        )

        # 테스트용 게시글과 댓글 생성
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article.",
            user=self.user,
        )
        self.comment = Comment.objects.create(
            content="This is a test comment.",
            article=self.article,
            user=self.user,
        )

        # 테스트용 신고 생성
        self.article_report = ArticleReport.objects.create(
            reporter=self.user2,
            reported_user=self.user,
            reported_article=self.article,
            report_detail="This is a test report.",
        )
        self.comment_report = CommentReport.objects.create(
            reporter=self.user2,
            reported_user=self.user,
            reported_comment=self.comment,
            report_detail="This is a test report.",
        )

    def get_access_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_admin_can_change_superuser_status(self):
        url = reverse("change-user-role", kwargs={"id": self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.put(url, {"is_superuser": "True"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_superuser)

    def test_admin_can_get_all_users(self):
        url = reverse("user-list-admin")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_admin_can_retrieve_user(self):
        url = reverse("user-detail-admin", kwargs={"id": self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)

    def test_admin_can_update_user(self):
        url = reverse("user-detail-admin", kwargs={"id": self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.put(url, {"username": "newusername"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")

    def test_admin_can_delete_user(self):
        url = reverse("user-detail-admin", kwargs={"id": self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_admin_can_retrieve_article(self):
        url = reverse("article-detail-admin", kwargs={"id": self.article.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["article_id"], self.article.id)

    def test_admin_can_delete_article(self):
        url = reverse("article-detail-admin", kwargs={"id": self.article.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_admin_can_retrieve_comment(self):
        url = reverse("comment-detail-admin", kwargs={"id": self.comment.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.comment.id)

    def test_admin_can_delete_comment(self):
        url = reverse("comment-detail-admin", kwargs={"id": self.comment.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_admin_can_update_article_report_status(self):
        url = reverse(
            "article-report-status-update",
            kwargs={"pk": self.article_report.id},
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.patch(url, {"status": "IP"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article_report.refresh_from_db()
        self.assertEqual(self.article_report.status, "IP")

    def test_admin_can_update_comment_report_status(self):
        url = reverse(
            "comment-report-status-update",
            kwargs={"pk": self.comment_report.id},
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.patch(url, {"status": "IP"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment_report.refresh_from_db()
        self.assertEqual(self.comment_report.status, "IP")

    def test_admin_can_get_all_reports(self):
        url = reverse("report-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("article_reports", response.data)
        self.assertIn("comment_reports", response.data)
        self.assertEqual(len(response.data["article_reports"]), 1)
        self.assertEqual(len(response.data["comment_reports"]), 1)

    def test_warning_count_increase_on_resolved_report(self):
        self.article_report.status = "RS"
        self.article_report.save()

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.warning_count, 1)

    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()
        self.comment.delete()
        self.article.delete()


class UserStatusTest(APITestCase):

    def setUp(self):
        # 일반 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            nickname="testnickname",
        )

        # 관리자 유저 생성
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="adminuser@example.com",
            password="adminpassword",
            nickname="adminnickname",
        )

    def authenticate(self, user):
        # JWT 토큰 생성 및 설정
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def test_user_status_for_normal_user(self):
        # 일반 유저로 인증
        self.authenticate(self.user)

        # 요청 보내기
        response = self.client.get("/api/auth/status/")

        # 일반 유저는 0을 반환
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], 0)

    def test_user_status_for_admin_user(self):
        # 관리자 유저로 인증
        self.authenticate(self.admin_user)

        # 요청 보내기
        response = self.client.get("/api/auth/status/")

        # 관리자 유저는 1을 반환
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], 1)

    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()
