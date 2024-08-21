from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Profile
from ..serializers import ProfileSerializer

User = get_user_model()


# 타인도 열람 가능한 유저 프로필 조회
class PublicUserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "유저를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        # 특정 필드만 선택적으로 직렬화
        serializer = ProfileSerializer(
            profile,
            fields=[
                "profile_image",
                "bio",
                "nickname",
                "selected_tags",
                "hunsoo_level",
            ],
        )

        # response_data = serializer.data
        # response_data["nickname"] = profile.user.nickname

        return Response(serializer.data, status=status.HTTP_200_OK)
