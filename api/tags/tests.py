from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tags.models import Tag


class TagListViewTest(APITestCase):
    def setUp(self):

        self.url = reverse("tag-list")

        Tag.objects.create(tag_id=0, name="전체")
        Tag.objects.create(tag_id=1, name="일상")
        Tag.objects.create(tag_id=2, name="연애 훈수")
        Tag.objects.create(tag_id=3, name="집안일 훈수")
        Tag.objects.create(tag_id=4, name="고민 훈수")
        Tag.objects.create(tag_id=5, name="소소 훈수")
        Tag.objects.create(tag_id=6, name="상상 훈수")
        Tag.objects.create(tag_id=7, name="패션 훈수")
        Tag.objects.create(tag_id=8, name="게임")
        Tag.objects.create(tag_id=9, name="모바일 게임 훈수")
        Tag.objects.create(tag_id=10, name="PC 게임 훈수")
        Tag.objects.create(tag_id=11, name="교육 훈수")

    def test_get_tag_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 12)

        expected_tags = [
            "전체",
            "일상",
            "연애 훈수",
            "집안일 훈수",
            "고민 훈수",
            "소소 훈수",
            "상상 훈수",
            "패션 훈수",
            "게임",
            "모바일 게임 훈수",
            "PC 게임 훈수",
            "교육 훈수",
        ]
