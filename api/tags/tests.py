from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Tag


class TagListViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # 테스트용 태그 생성
        self.tag1 = Tag.objects.create(name="연애 훈수")
        self.tag2 = Tag.objects.create(name="집안일 훈수")
        self.tag3 = Tag.objects.create(name="고민 훈수")

        # 테스트할 URL
        self.url = "/api/tag/list/"

    def test_get_tag_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 생성된 태그의 개수를 확인
        self.assertEqual(response.data[0]["name"], "연애 훈수")
        self.assertEqual(response.data[1]["name"], "집안일 훈수")
        self.assertEqual(response.data[2]["name"], "고민 훈수")

    def tearDown(self):
        # 테스트 후 데이터 정리
        Tag.objects.all().delete()
