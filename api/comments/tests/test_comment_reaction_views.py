from articles.models import Article
from comments.models import Comment, CommentReaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class CommentReactionTests(APITestCase):

    def setUp(self):
        # 테스트 유저와 게시글, 댓글 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            nickname="TestNickname",
        )
        self.article = Article.objects.create(
            user=self.user, title="Test Article", content="Test Content"
        )
        self.comment = Comment.objects.create(
            user=self.user, article=self.article, content="Test Comment"
        )

        # 작성자가 아닌 다른 유저 생성
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpassword",
            nickname="OtherNickname",
        )

        # JWT 토큰 생성 및 설정
        self.client.force_authenticate(user=self.user)

        # 도움이 돼요/안돼요 토글 URL
        self.reaction_url = reverse(
            "comment-reaction-toggle", kwargs={"pk": self.comment.id}
        )

    def test_author_cannot_react_to_own_comment(self):
        # 작성자가 자신의 댓글에 반응을 시도할 때
        data = {"reaction_type": "helpful"}
        response = self.client.post(self.reaction_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "You cannot react to your own comment."
        )

        # 다른 유저가 댓글에 반응하는 경우
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.reaction_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            CommentReaction.objects.filter(
                comment=self.comment, reaction_type="helpful"
            ).count(),
            1,
        )

    def test_toggle_helpful_reaction(self):
        # 도움이 돼요 반응 추가 테스트
        self.client.force_authenticate(user=self.other_user)
        data = {"reaction_type": "helpful"}
        response = self.client.post(self.reaction_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            CommentReaction.objects.filter(
                comment=self.comment, reaction_type="helpful"
            ).count(),
            1,
        )

        # 도움이 돼요 반응 제거 테스트
        response = self.client.post(self.reaction_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            CommentReaction.objects.filter(
                comment=self.comment, reaction_type="helpful"
            ).count(),
            0,
        )

    def test_toggle_not_helpful_reaction(self):
        # 안돼요 반응 추가 테스트
        self.client.force_authenticate(user=self.other_user)
        data = {"reaction_type": "not_helpful"}
        response = self.client.post(self.reaction_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            CommentReaction.objects.filter(
                comment=self.comment, reaction_type="not_helpful"
            ).count(),
            1,
        )

        # 안돼요 반응 제거 테스트
        response = self.client.post(self.reaction_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            CommentReaction.objects.filter(
                comment=self.comment, reaction_type="not_helpful"
            ).count(),
            0,
        )

    def tearDown(self):
        self.user.delete()
        self.article.delete()
        self.comment.delete()
