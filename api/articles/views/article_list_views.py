from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework import generics

from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..models import Article
from ..serializers import ArticleDetailSerializer, ArticleListSerializer

# 게시글 상세정보 조회
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "id"


# 전체 게시글 조회 리스트
class ArticleListView(generics.ListAPIView):
    queryset = (
        Article.objects.select_related("user")
        .prefetch_related("tags", "images")
        .order_by("-created_at")
    )
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        
        cache_key = "article_list_cache_key"

        # 캐시에서 데이터 가져오기
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # 캐시된 데이터가 없으면 쿼리 실행 후 캐시에 저장
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # 응답 객체에 렌더러 설정
        response = Response(data)
        response.accepted_renderer = self.request.accepted_renderer
        response.accepted_media_type = self.request.accepted_media_type
        response.renderer_context = self.get_renderer_context()
        
        response.render()
        cache.set(cache_key, response.data, 60 * 15)  # 15분 동안 캐시 유지
        return response


# 특정 태그별 게시글 조회 리스트
class ArticleByTagView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        tag_id = self.kwargs["tag_id"]
        return Article.objects.filter(tags__tag_id=tag_id).order_by("-created_at")


# 전체 게시글 조회 리스트 (like 상태와 article_id만 반환)
class ArticleLikeListView(generics.ListAPIView):
    queryset = Article.objects.all().order_by("-created_at")
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )

        # 필요한 응답 형식으로 변환
        response_data = []
        for article_data in serializer.data:
            response_data.append(
                {"like": article_data["like"], "article_id": article_data["article_id"]}
            )

        return Response(response_data)
