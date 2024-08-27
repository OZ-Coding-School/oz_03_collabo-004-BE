from articles.models import Article, ArticleImage
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from tags.models import Tag
from users.models import User


class ArticleCRUDTests(APITestCase):

    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            nickname="TestNickname",
        )
        # JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # 쿠키에 토큰 설정
        self.client.cookies["access"] = self.access_token
        self.client.cookies["refresh"] = self.refresh_token

        # 테스트 태그 생성
        self.tag1 = Tag.objects.create(tag_id=0, name="연애 훈수")
        self.tag2 = Tag.objects.create(tag_id=1, name="집안일 훈수")
        self.tag3 = Tag.objects.create(tag_id=2, name="고민 훈수")

        # 게시글 작성에 사용할 데이터
        self.article_data = {
            "title": "Test Article",
            "content": "This is a test article.",
            "tag_ids": [self.tag1.tag_id, self.tag2.tag_id],
        }

        # 게시글 생성 URL
        self.create_url = reverse("article-create")

    def test_create_article(self):
        # 게시글 생성 테스트
        response = self.client.post(self.create_url, self.article_data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.first().title, "Test Article")

    def test_update_article(self):
        # 게시글 생성
        article = Article.objects.create(
            user=self.user, title="Old Title", content="Old content"
        )
        update_url = reverse("article-update", kwargs={"id": article.id})

        # 수정할 데이터
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "tag_ids": [self.tag1.tag_id, self.tag3.tag_id],
        }

        # 게시글 수정 테스트
        response = self.client.put(update_url, update_data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 수정 결과 확인
        article.refresh_from_db()
        self.assertEqual(article.title, "Updated Title")
        self.assertEqual(article.content, "Updated content")

    def test_delete_article(self):
        # 게시글 생성
        article = Article.objects.create(
            user=self.user, title="Title to be deleted", content="Content to be deleted"
        )
        delete_url = reverse("article-delete", kwargs={"id": article.id})

        # 게시글 삭제 테스트
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)

    def test_retrieve_article(self):
        # 게시글 생성
        article = Article.objects.create(
            user=self.user,
            title="Title to be retrieved",
            content="Content to be retrieved",
        )
        retrieve_url = reverse("article-detail", kwargs={"id": article.id})

        # 게시글 조회 테스트
        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], article.title)
        self.assertEqual(response.data["content"], article.content)

    def tearDown(self):
        self.user.delete()
        Tag.objects.all().delete()
        Article.objects.all().delete()


class ArticleListTests(APITestCase):

    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            nickname="TestNickname",
        )
        # JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # 쿠키에 토큰 설정
        self.client.cookies["access"] = self.access_token
        self.client.cookies["refresh"] = self.refresh_token

        # 테스트 태그 생성
        self.tag1 = Tag.objects.create(tag_id=0, name="연애 훈수")
        self.tag2 = Tag.objects.create(tag_id=1, name="집안일 훈수")
        self.tag3 = Tag.objects.create(tag_id=2, name="고민 훈수")

        # 추가로 몇 개의 게시글을 더 생성
        self.article1 = Article.objects.create(
            user=self.user, title="Article 1", content="Content 1"
        )
        self.article2 = Article.objects.create(
            user=self.user, title="Article 2", content="Content 2"
        )
        self.article1.tags.add(self.tag1, self.tag2)
        self.article2.tags.add(self.tag2, self.tag3)

    def test_list_all_articles(self):
        # 전체 게시글 조회 URL
        list_url = reverse("article-list")

        # 전체 게시글 조회 테스트
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Article 1")
        self.assertEqual(response.data[1]["title"], "Article 2")

    def tearDown(self):
        self.user.delete()
        Tag.objects.all().delete()
        Article.objects.all().delete()


class ArticleByTagTests(APITestCase):

    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            nickname="TestNickname",
        )
        # JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # 쿠키에 토큰 설정
        self.client.cookies["access"] = self.access_token
        self.client.cookies["refresh"] = self.refresh_token

        # 테스트 태그 생성
        self.tag1 = Tag.objects.create(tag_id=0, name="연애 훈수")
        self.tag2 = Tag.objects.create(tag_id=1, name="집안일 훈수")
        self.tag3 = Tag.objects.create(tag_id=2, name="고민 훈수")

        # 추가로 몇 개의 게시글을 더 생성
        self.article1 = Article.objects.create(
            user=self.user, title="Article 1", content="Content 1"
        )
        self.article2 = Article.objects.create(
            user=self.user, title="Article 2", content="Content 2"
        )
        self.article1.tags.add(self.tag1, self.tag2)
        self.article2.tags.add(self.tag2, self.tag3)

    def test_list_articles_by_tag(self):
        # 태그별 게시글 조회 URL
        tag_url = reverse("articles-by-tag", kwargs={"tag_id": self.tag2.tag_id})

        # 태그로 필터링된 게시글 조회 테스트
        response = self.client.get(tag_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # tag2에 속하는 게시글이 2개 있어야 함
        self.assertIn("Article 1", [article["title"] for article in response.data])
        self.assertIn("Article 2", [article["title"] for article in response.data])

        # 특정 태그에 속한 게시글 조회 테스트 (tag1)
        tag1_url = reverse("articles-by-tag", kwargs={"tag_id": self.tag1.tag_id})
        response = self.client.get(tag1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # tag1에 속하는 게시글이 1개 있어야 함
        self.assertEqual(response.data[0]["title"], "Article 1")

        # 특정 태그에 속한 게시글이 없는 경우 테스트 (없는 태그)
        non_existing_tag_url = reverse("articles-by-tag", kwargs={"tag_id": 999})
        response = self.client.get(non_existing_tag_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 0
        )  # 존재하지 않는 태그에 대한 게시글은 0개여야 함

    def tearDown(self):
        self.user.delete()
        Tag.objects.all().delete()
        Article.objects.all().delete()
