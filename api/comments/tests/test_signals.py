import os

from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AiHunsooSignalTest(TestCase):

    def setUp(self):

        # User 객체 생성
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
            nickname="testnickname",
            social_platform="general",
        )

        # User2 객체 생성
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            username="testuser2",
            password="testpassword2",
            nickname="testnickname2",
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

        # Comment 객체 생성 시, user 필드에 self.user2 할당
        self.comment = Comment.objects.create(
            user=self.user2, article=self.article, content="This is a test comment."
        )

    def test_create_ai_hunsoo_signal(self):
        # 처음에는 AiHunsoo 객체가 없는지 확인
        self.assertEqual(AiHunsoo.objects.count(), 0)

        # 댓글의 is_selected 필드를 True로 변경하여 저장
        self.comment.is_selected = True
        self.comment.save()

        # 시그널 핸들러에 의해 AiHunsoo 객체가 생성되었는지 확인
        self.assertEqual(AiHunsoo.objects.count(), 1)

        # 생성된 AiHunsoo 객체의 내용을 확인
        ai_hunsoo = AiHunsoo.objects.first()
        self.assertEqual(ai_hunsoo.article, self.article)
        self.assertIn("This is a test article.", ai_hunsoo.content)
        self.assertIn("This is a test comment.", ai_hunsoo.content)
