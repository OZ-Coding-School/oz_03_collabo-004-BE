from articles.models import Article
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class ArticleReactionTests(APITestCase):

    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            nickname="TestNickname",
        )
        # JWT 토큰 생성
        self.client.force_authenticate(user=self.user)

        # 테스트 게시글 생성
        self.article = Article.objects.create(
            user=self.user, title="Test Article", content="Test Content"
        )

        self.view_url = reverse("article-view-count", kwargs={"id": self.article.id})
        self.like_url = reverse("article-like", kwargs={"id": self.article.id})

    def test_view_count_increase(self):
        # 초기 조회수 확인
        initial_view_count = self.article.view_count

        # 첫 번째 조회 요청 (GET)
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 조회수 증가 확인
        self.article.refresh_from_db()
        self.assertEqual(self.article.view_count, initial_view_count + 1)

        # 동일한 세션에서 두 번째 조회 요청 (GET)
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 조회수는 증가하지 않아야 함
        self.article.refresh_from_db()
        self.assertEqual(self.article.view_count, initial_view_count + 1)

        # 다른 세션에서 조회 (로그아웃 후 로그인)
        self.client.logout()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 조회수 다시 증가 확인
        self.article.refresh_from_db()
        self.assertEqual(self.article.view_count, initial_view_count + 2)

    def test_like_toggle(self):
        # 초기 좋아요 개수 확인
        initial_like_count = self.article.like_count

        # 첫 번째 좋아요 요청 (추가)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.like_count, initial_like_count + 1)

        # 두 번째 좋아요 요청 (삭제)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.like_count, initial_like_count)

    def tearDown(self):
        self.user.delete()
        self.article.delete()
