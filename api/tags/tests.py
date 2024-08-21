from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tags.models import Tag


class TagListViewTest(APITestCase):
    def setUp(self):
        # 기본적으로 저장된 태그들이 DB에 존재하는지 확인합니다.
        self.url = reverse("tag-list")  # 태그 리스트를 반환하는 API URL

        Tag.objects.create(tag_id=0, name="연애 훈수")
        Tag.objects.create(tag_id=1, name="집안일 훈수")
        Tag.objects.create(tag_id=2, name="고민 훈수")
        Tag.objects.create(tag_id=3, name="소소 훈수")
        Tag.objects.create(tag_id=4, name="상상 훈수")
        Tag.objects.create(tag_id=5, name="패션 훈수")
        Tag.objects.create(tag_id=6, name="게임 훈수")
        Tag.objects.create(tag_id=7, name="교육 훈수")

    def test_get_tag_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)  # 고정된 태그가 8개이므로

        expected_tags = [
            "연애 훈수",
            "집안일 훈수",
            "고민 훈수",
            "소소 훈수",
            "상상 훈수",
            "패션 훈수",
            "게임 훈수",
            "교육 훈수",
        ]

        for tag_data, expected_name in zip(response.data, expected_tags):
            self.assertEqual(tag_data["name"], expected_name)
