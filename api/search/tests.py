from time import sleep

from articles.models import Article
from django.contrib.auth import get_user_model
from django.test import TestCase
from elasticsearch_dsl import connections
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class ArticleSearchTests(TestCase):
    def setUp(self):

        self.es = connections.get_connection()
        self.es.indices.delete(index='articles', ignore=[400, 404])

        # API 클라이언트 초기화
        self.client = APIClient()

        # 테스트에 사용할 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            nickname="TestNickname",
        )

        # 테스트에 사용할 게시글 생성
        self.article1 = Article.objects.create(
            user=self.user,
            title="Django Testing",
            content="This is a test article about Django testing.",
        )

        self.article2 = Article.objects.create(
            user=self.user,
            title="REST Framework",
            content="Testing the Django REST framework with elasticsearch.",
        )

        self.article3 = Article.objects.create(
            user=self.user,
            title="Elasticsearch",
            content="Elasticsearch integration testing in Django.",
        )

        # Elasticsearch 인덱싱 대기 시간
        sleep(1)

    def tearDown(self):
        # 테스트 후 Elasticsearch 인덱스 삭제
        self.es.indices.delete(index="articles", ignore=[400, 404])

    def test_search_query_django(self):
        response = self.client.get("/api/search/", {"q": "Django"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Django Testing")

    def test_search_query_rest_framework(self):
        response = self.client.get("/api/search/", {"q": "REST"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "REST Framework")

    def test_search_query_elasticsearch(self):
        response = self.client.get("/api/search/", {"q": "Elasticsearch"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Elasticsearch")

    def test_search_query_no_results(self):
        response = self.client.get("/api/search/", {"q": "NoMatch"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_query_missing_q_parameter(self):
        response = self.client.get("/api/search/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "검색어를 입력하세요.")
