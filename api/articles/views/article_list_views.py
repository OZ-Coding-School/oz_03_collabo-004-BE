from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..models import Article
from ..serializers import ArticleDetailSerializer, ArticleListSerializer


# 페이지네이션 1페이지당 12개 게시물
class ArticlePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


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
    pagination_class = ArticlePagination

    def list(self, request, *args, **kwargs):
        # 페이지 번호를 캐시 키에 포함
        page_number = request.query_params.get("page", 1)
        cache_key = f"article_list_page_{page_number}"

        # 캐시에서 데이터 가져오기
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # 캐시된 데이터가 없으면 쿼리 실행 후 캐시에 저장
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data)

            # 응답 객체에 렌더러 설정
            data.accepted_renderer = self.request.accepted_renderer
            data.accepted_media_type = self.request.accepted_media_type
            data.renderer_context = self.get_renderer_context()

            data.render()
            cache.set(cache_key, data.data, 60 * 15)  # 15분 동안 캐시 유지
            return data

        return Response({"detail": "No articles found."}, status=404)


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
