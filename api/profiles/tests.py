import json

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile

User = get_user_model()


class UpdateHunsooLevelTest(APITestCase):
    def setUp(self):
        # APIClient 초기화
        self.client = APIClient()

        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
            nickname="testnickname",
            social_platform="general",
        )
        self.profile = Profile.objects.create(user=self.user, hunsoo_level=1)

        # JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # 쿠키에 토큰 설정
        self.client.cookies["access"] = self.access_token
        self.client.cookies["refresh"] = self.refresh_token

        # 테스트할 URL
        self.url = "/api/account/level/"

    def test_update_hunsoo_level_success(self):
        # 유효한 데이터로 요청을 보냄
        data = {"hunsoo_level": 3}
        response = self.client.put(self.url, data, format="json")

        # 성공적으로 업데이트가 되었는지 확인
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.hunsoo_level, 3)

    def test_update_hunsoo_level_invalid_data(self):
        # 유효하지 않은 데이터를 보냄 (예: 음수 레벨)
        data = {"hunsoo_level": -1}
        response = self.client.put(self.url, data, format="json")

        # 오류가 발생했는지 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_hunsoo_level_unauthenticated(self):
        # 인증 없이 요청을 보내도록 클라이언트 쿠키 삭제
        self.client.cookies.clear()

        # 요청을 보냄
        data = {"hunsoo_level": 3}
        response = self.client.put(self.url, data, format="json")

        # 접근이 거부되었는지 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        # 테스트 후 데이터 정리
        self.user.delete()
        self.profile.delete()
