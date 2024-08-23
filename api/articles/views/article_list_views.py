from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..models import Article
from ..serializers import ArticleListSerializer, ArticleSerializer


# 게시글 상세정보 조회
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"


# 전체 게시글 조회 리스트
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]


# 특정 태그별 게시글 조회 리스트
class ArticleByTagView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        tag_id = self.kwargs["tag_id"]
        return Article.objects.filter(tags__tag_id=tag_id)
