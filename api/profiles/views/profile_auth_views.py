from articles.models import Article
from articles.serializers import ArticleListSerializer
from comments.models import Comment
from comments.serializers import CommentListSerializer
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tags.serializers import TagSerializer

from ..models import Profile
from ..serializers import ProfileSerializer


# 사용자 프로필 조회
class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 사용자 프로필 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        user = request.user

        # 닉네임 업데이트
        new_nickname = request.data.get("nickname")
        if new_nickname:
            user.nickname = new_nickname
            user.save()

        # 프로필 업데이트
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
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
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # profile serializer의 훈수레벨 읽기 전용 필드를 해제하여, 특정 상황에서만 수정 가능하게 함
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.fields["hunsoo_level"].read_only = False

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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
