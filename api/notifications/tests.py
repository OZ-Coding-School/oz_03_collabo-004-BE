from articles.models import Article
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from notifications.models import Notification
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class NotificationTests(APITestCase):

    def setUp(self):
        # 테스트용 유저 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password123",
            nickname="publicnickname",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password123",
            nickname="publicnickname",
        )

        # JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(self.refresh.access_token)

        # 테스트용 게시글 및 댓글 생성
        self.article = Article.objects.create(
            user=self.user1, title="Test Article", content="Test Content"
        )
        self.comment = Comment.objects.create(
            user=self.user2, article=self.article, content="Test Comment"
        )

        # 테스트용 알림 생성 전에 자동 생성된 알림이 있는지 확인
        self.initial_notification_count = Notification.objects.count()

        # 테스트용 알림 생성
        self.notification = Notification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            verb="comment",
            content_type=ContentType.objects.get_for_model(self.comment),
            object_id=self.comment.id,
            article=self.article,
        )

        # 테스트용 알림 생성 후의 알림 개수 확인
        self.post_creation_notification_count = Notification.objects.count()

        # 자동 생성된 알림 개수와 테스트용 알림 개수 확인
        self.generated_notification_count = (
            self.post_creation_notification_count - self.initial_notification_count
        )

    def test_notification_list(self):
        # 알림 목록 조회 테스트
        url = reverse("notification-list")  # 알림 목록 조회를 위한 URL
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 총 알림 개수 중 자동 생성된 알림을 포함해서 비교
        expected_count = (
            self.initial_notification_count + 1
        )  # 수동으로 생성한 알림 1개 포함
        self.assertEqual(
            self.generated_notification_count,
            expected_count - self.initial_notification_count,
        )
        self.assertEqual(len(response.data), expected_count)

    def test_notification_detail(self):
        """특정 알림의 세부 정보 조회 테스트"""
        url = reverse("notification-detail", kwargs={"pk": self.notification.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.notification.id)

    def test_mark_notification_as_read(self):
        """알림을 읽음 상태로 변경하는 테스트"""
        url = reverse("notification-mark-as-read", kwargs={"pk": self.notification.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.read)

    def test_delete_notification(self):
        """특정 알림을 삭제하는 테스트"""
        url = reverse("notification-delete", kwargs={"pk": self.notification.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(id=self.notification.id).exists())

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.comment.delete()
        self.article.delete()
        self.notification.delete()
