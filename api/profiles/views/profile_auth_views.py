from articles.models import Article
from articles.serializers import ArticleListSerializer
from comments.models import Comment
from comments.serializers import CommentListSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from tags.serializers import TagSerializer
from users.models import User

from ..models import Profile
from ..serializers import ProfileSerializer


# 사용자 프로필 조회
class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id=None):
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            user = request.user

        profile, created = Profile.objects.get_or_create(user=user)
        is_own_profile = user == request.user

        serializer = ProfileSerializer(
            profile, context={"is_own_profile": is_own_profile}
        )
        response_data = serializer.data
        response_data["status"] = is_own_profile

        return Response(response_data, status=status.HTTP_200_OK)


# 사용자 프로필 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        user = request.user

        serializer = ProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            # 수정된 필드만 응답으로 반환
            updated_data = {}
            for field in request.data.keys():
                if field == "selected_tags":
                    # 태그 필드 처리
                    updated_data[field] = TagSerializer(
                        profile.selected_tags.all(), many=True
                    ).data
                elif field == "nickname":
                    # 닉네임은 user 객체에서 가져오기
                    updated_data[field] = user.nickname
                else:
                    updated_data[field] = serializer.validated_data.get(field)

            return Response(updated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 유저 레벨 수정
class UserLevelUpdate(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get("id")  # URL에서 유저 ID를 가져옴
        profile = get_object_or_404(
            Profile, user__id=user_id
        )  # 해당 유저의 프로필 조회

        new_level = request.data.get(
            "hunsoo_level"
        )  # 클라이언트로부터 레벨 정보 받아옴

        if new_level is None:
            return Response(
                {"error": "훈수레벨값을 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_level = int(new_level)  # 레벨이 정수인지 확인
        except ValueError:
            return Response(
                {"error": "정수값을 입력해야합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 훈수레벨이 1에서 20 사이의 정수인지 검증
        if new_level < 1 or new_level > 20:
            return Response(
                {"error": "1-20사이의 값을 입력해야합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # profile serializer의 훈수레벨 읽기 전용 필드를 해제하여, 수정 가능하게 함
        serializer = ProfileSerializer(
            profile, data={"hunsoo_level": new_level}, partial=True
        )
        serializer.fields["hunsoo_level"].read_only = False  # 읽기 전용 해제

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"hoonsu_level": serializer.data["hunsoo_level"]},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 유저가 작성한 게시글 목록
class UserArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)


# 유저가 작성한 댓글(훈수) 목록
class UserCommentListView(generics.ListAPIView):
    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
