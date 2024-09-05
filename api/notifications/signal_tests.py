from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from django.test import TestCase
from notifications.models import Notification
from users.models import User


class CommentNotificationTest(TestCase):
    def setUp(self):
        # 테스트용 유저 및 게시글 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.article = Article.objects.create(
            user=self.user1, title="Test Article", content="Test Content"
        )

    def test_comment_notification(self):
        # 댓글 작성
        Comment.objects.create(
            user=self.user2, article=self.article, content="Test Comment"
        )

        # 알림이 생성되었는지 확인
        notification = Notification.objects.get(recipient=self.user1, verb="comment")
        self.assertIsNotNone(notification)
        self.assertEqual(notification.actor, self.user2)
        self.assertEqual(notification.target.article, self.article)


class LikeNotificationTest(TestCase):
    def setUp(self):
        # 테스트용 유저 및 게시글 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.article = Article.objects.create(
            user=self.user1, title="Test Article", content="Test Content"
        )

    def test_like_notification(self):
        # 좋아요 추가
        self.article.likes.add(self.user2)

        # 알림이 생성되었는지 확인
        notification = Notification.objects.get(recipient=self.user1, verb="like")
        self.assertIsNotNone(notification)
        self.assertEqual(notification.actor, self.user2)
        self.assertEqual(notification.target, self.article)


class CommentSelectionNotificationTest(TestCase):
    def setUp(self):
        # 테스트용 유저 및 게시글 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.article = Article.objects.create(
            user=self.user1, title="Test Article", content="Test Content"
        )
        self.comment = Comment.objects.create(
            user=self.user2, article=self.article, content="Test Comment"
        )

    def test_comment_selection_notification(self):
        # 댓글 채택
        self.comment.is_selected = True
        self.comment.save()

        # 알림이 생성되었는지 확인
        notification = Notification.objects.get(recipient=self.user2, verb="select")
        self.assertIsNotNone(notification)
        self.assertEqual(notification.actor, self.user1)
        self.assertEqual(notification.target, self.comment)


class AiResponseNotificationTest(TestCase):
    def setUp(self):
        # 테스트용 유저 및 게시글 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            nickname="publicnickname",
        )
        self.article = Article.objects.create(
            user=self.user1, title="Test Article", content="Test Content"
        )

    def test_ai_response_notification(self):
        # AI 댓글 생성
        AiHunsoo.objects.create(article=self.article, content="AI Response")

        # 알림이 생성되었는지 확인
        notification = Notification.objects.get(
            recipient=self.user1, verb="ai_response"
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.actor, None)  # AI는 actor가 없음
        self.assertEqual(notification.target.article, self.article)
