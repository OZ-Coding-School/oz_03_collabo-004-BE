import json

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from tags.models import Tag

from .models import Profile

User = get_user_model()


class UpdateHunsooLevelTest(APITestCase):
    def setUp(self):
        # APIClient 초기화
        self.client = APIClient()

        # 어드민 사용자 생성
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            username="adminuser",
            password="adminpassword",
            nickname="adminnickname",
            social_platform="general",
        )

        # 일반 사용자 생성
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
            nickname="testnickname",
            social_platform="general",
        )
        self.profile = Profile.objects.get(user=self.user)

        # 어드민 JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # 쿠키에 어드민 토큰 설정
        self.client.cookies["hunsu_access"] = self.access_token
        self.client.cookies["hunsu_refresh"] = self.refresh_token

        # 테스트할 URL (조정당하는 일반 유저의 ID 사용)
        self.url = f"/api/account/level/{self.user.id}/"

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

        # 인증 오류가 발생했는지 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()


class UserProfileDetailTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # 테스트용 사용자 및 프로필 생성
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword",
            nickname="testnickname",
            social_platform="general",
        )
        self.profile = Profile.objects.get(
            user=self.user)
        self.profile.bio="This is a test bio."
        self.profile.save()

        # 닉네임 중복 테스트를 위해 추가 사용자 생성
        self.user2 = User.objects.create_user(
            email="duplicate@example.com",
            username="duplicateuser",
            password="testpassword",
            nickname="duplicatenickname",
            social_platform="general",
        )
        self.profile2 = Profile.objects.get(
            user=self.user2)
        self.profile2.hunsoo_level = 2
        self.profile2.bio="This is another test bio."
        self.profile2.save()

        # JWT 토큰 생성
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # 쿠키에 토큰 설정
        self.client.cookies["hunsu_access"] = self.access_token
        self.client.cookies["hunsu_refresh"] = self.refresh_token

        # 테스트할 URL
        self.url = "/api/account/profile/"
        self.profile_update_url = "/api/account/profile/update/"

    def test_get_user_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "testnickname")
        self.assertEqual(response.data["hunsoo_level"], 1)
        self.assertEqual(response.data["bio"], "This is a test bio.")
        self.assertTrue(response.data["status"])

    def test_get_other_user_profile(self):
        # 다른 사용자의 프로필을 조회하는 테스트
        url = f"/api/account/profile/{self.user2.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "duplicatenickname")
        self.assertEqual(response.data["hunsoo_level"], 2)
        self.assertEqual(response.data["bio"], "This is another test bio.")
        self.assertFalse(response.data["status"])

    def test_update_user_profile_bio(self):
        # 프로필 바이오 수정 테스트
        data = {"bio": "Updated bio"}
        response = self.client.put(self.profile_update_url, data, format="json")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.bio, "Updated bio")

    def test_update_user_profile_nickname(self):
        # 닉네임 수정 테스트
        data = {"nickname": "NewNickname"}
        response = self.client.put(self.profile_update_url, data, format="json")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.user.nickname, "NewNickname")

    def test_update_user_profile_nickname_with_duplicate(self):
        # 닉네임 중복 수정 테스트
        data = {"nickname": "duplicatenickname"}  # 이미 존재하는 닉네임 사용
        response = self.client.put(self.profile_update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("이미 사용 중인 닉네임입니다.", response.data["nickname"])

    def test_update_user_profile_tags(self):
        # 사용자 태그 수정 테스트
        tag1 = Tag.objects.create(tag_id=1, name="Tag1")
        tag2 = Tag.objects.create(tag_id=2, name="Tag2")
        tag3 = Tag.objects.create(tag_id=3, name="Tag3")

        data = {"selected_tags": [tag1.tag_id, tag2.tag_id, tag3.tag_id]}
        response = self.client.put(self.profile_update_url, data, format="json")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(self.profile.selected_tags.all()), [tag1, tag2, tag3])

    # def test_unauthenticated_user_profile_access(self):
    #     self.client.cookies.clear()
    #     response = self.client.get(self.url)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        self.user.delete()
        self.profile.delete()
        self.user2.delete()
        self.profile2.delete()
