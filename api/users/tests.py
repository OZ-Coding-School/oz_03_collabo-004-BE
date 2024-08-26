from articles.models import Article
from comments.models import Comment
from django.urls import reverse
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

    def test_admin_can_delete_user_articles_comments(self):
        url = reverse(
            "user-delete-articles-comments-admin", kwargs={"id": self.user.id}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(user=self.user).exists())
        self.assertFalse(Comment.objects.filter(user=self.user).exists())
