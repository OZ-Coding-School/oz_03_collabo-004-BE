from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AiHunsooDetailViewTest(TestCase):

    def setUp(self):
        # User 객체 생성
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
            nickname="testnickname",
            social_platform="general",
        )

        # Article 객체 생성 시, user 필드에 self.user 할당
        self.article = Article.objects.create(
            user=self.user,
            title="Test Article",
            content="This is a test article.",
            is_closed=False,
            view_count=0,
        )

        # AiHunsoo 객체 생성
        self.ai_hunsoo = AiHunsoo.objects.create(
            article=self.article, content="This is an AI generated response."
        )

        self.client = APIClient()

    def test_get_ai_hunsoo_success(self):
        url = f"/api/ai_hunsu/{self.article.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], self.ai_hunsoo.content)

    def test_get_ai_hunsoo_not_found(self):
        url = f"/api/ai_hunsu/9999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
