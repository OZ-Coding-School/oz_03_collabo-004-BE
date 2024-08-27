from articles.models import Article
from comments.models import Comment, CommentImage
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class CommentCRUDTests(APITestCase):

    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            nickname="TestNickname",
        )

        # JWT 토큰 생성 및 설정
        self.client.force_authenticate(user=self.user)

        # 테스트 게시글 생성
        self.article = Article.objects.create(
            user=self.user, title="Test Article", content="Test Content"
        )

        # 댓글 생성 URL
        self.create_url = reverse(
            "comment-create", kwargs={"article_id": self.article.id}
        )
        # 댓글 목록 조회 URL
        self.list_url = reverse("comment-list", kwargs={"article_id": self.article.id})
        # 댓글 상세 조회 URL
        self.comment = Comment.objects.create(
            user=self.user, article=self.article, content="Test Comment"
        )
        self.detail_url = reverse("comment-detail", kwargs={"pk": self.comment.id})
        # 댓글 수정 URL
        self.update_url = reverse("comment-update", kwargs={"pk": self.comment.id})

    def test_create_comment(self):
        # 댓글 생성 테스트
        new_user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="newpassword",
            nickname="NewUserNickname",
        )
        self.client.force_authenticate(user=new_user)

        data = {"content": "New Comment", "article": self.article.id}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().content, "New Comment")
        self.assertEqual(Comment.objects.first().article.id, self.article.id)

    def test_create_comment_by_article_owner(self):
        # 게시글 작성자가 댓글을 달려고 할 때 실패하는지 테스트
        data = {"content": "Owner's Comment"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.count(), 1)  # 기존 댓글 1개 그대로

    def test_create_comment_by_another_user(self):
        # 다른 사용자가 댓글을 달 수 있는지 테스트
        new_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="anotherpassword",
            nickname="AnotherNickname",
        )
        self.client.force_authenticate(user=new_user)

        data = {"content": "Another User's Comment"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().content, "Another User's Comment")

    def test_list_comments(self):
        # 댓글 목록 조회 테스트 (인증 없이 가능)
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Test Comment")

    def test_retrieve_comment(self):
        # 댓글 상세 조회 테스트 (인증 없이 가능)
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Test Comment")

    def test_update_comment(self):
        # 댓글 수정 테스트
        data = {"content": "Updated Comment", "article": self.article.id}
        response = self.client.put(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated Comment")
        self.assertEqual(self.comment.article.id, self.article.id)

    def test_update_comment_when_article_is_closed(self):
        # 게시글을 마감 상태로 변경
        self.article.is_closed = True
        self.article.save()

        # 댓글 수정 시도
        data = {"content": "Updated Comment"}
        response = self.client.put(self.update_url, data, format="json")

        # 403 Forbidden 응답이 반환되어야 함
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "이미 마감이 된 게시글에 대하여 수정할 수 없습니다.", str(response.data)
        )

    # ai 시그널이랑 연결되어 있어 요금 부과
    # def test_update_comment_when_other_comment_is_selected(self):
    #     # 기존 댓글을 선택된 상태로 만듦
    #     self.comment.is_selected = True
    #     self.comment.save()

    #     # 댓글 수정 시도
    #     data = {"content": "Updated Comment"}
    #     response = self.client.put(self.update_url, data, format="json")

    #     # 403 Forbidden 응답이 반환되어야 함
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn(
    #         "이 게시글의 다른 댓글이 이미 채택되었습니다.", str(response.data)
    #     )

    def test_update_comment_when_not_owner(self):
        # 다른 유저 생성
        another_user = User.objects.create_user(
            username="anotheruser",
            email="anotheruser@example.com",
            password="anotherpassword",
            nickname="AnotherUserNickname",
        )
        self.client.force_authenticate(user=another_user)

        # 댓글 수정 시도
        data = {"content": "Updated Comment"}
        response = self.client.put(self.update_url, data, format="json")

        # 403 Forbidden 응답이 반환되어야 함
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("댓글을 수정할 권한이 없습니다.", str(response.data))

    def tearDown(self):
        self.user.delete()
        self.article.delete()
        self.comment.delete()
