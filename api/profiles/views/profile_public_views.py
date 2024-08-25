from comments.models import Comment
from django.contrib.auth import get_user_model
from django.db.models import Count
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
            user = User.objects.get(username=username)
            profile, created = Profile.objects.get_or_create(user=user)
        except User.DoesNotExist:
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
                "selected_comment_count",
            ],
        )

        # response_data = serializer.data
        # response_data["nickname"] = profile.user.nickname

        # 채택된 댓글 수 계산
        selected_comment_count = Comment.objects.filter(
            user=profile.user, is_selected=True
        ).count()

        # 응답 데이터 구성
        response_data = serializer.data
        response_data["selected_comment_count"] = selected_comment_count

        return Response(response_data, status=status.HTTP_200_OK)
