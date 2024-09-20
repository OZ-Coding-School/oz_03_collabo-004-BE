from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
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

    @method_decorator(cache_page(60 * 15))  # 15분 동안 캐시
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


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
