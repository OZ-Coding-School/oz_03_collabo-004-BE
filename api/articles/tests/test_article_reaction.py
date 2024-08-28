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

        # 작성자가 아닌 다른 유저 생성
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword",
            nickname="OtherNickname",
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

    def test_author_cannot_like_own_article(self):
        # 게시글 작성자가 자신의 게시글에 좋아요를 시도하는 경우
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"], "게시글 작성자는 좋아요를 누를 수 없습니다."
        )

    def test_other_user_can_like_article(self):
        # 작성자가 아닌 다른 사용자가 좋아요를 시도하는 경우
        self.client.force_authenticate(user=self.other_user)

        # 첫 번째 좋아요 요청 (추가)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.like_count, 1)

        # 두 번째 좋아요 요청 (삭제)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.like_count, 0)

    def tearDown(self):
        self.user.delete()
        self.article.delete()
