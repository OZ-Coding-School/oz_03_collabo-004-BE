from rest_framework import generics
from ..models import Article
from ..serializers import ArticleSerializer, ArticleListSerializer

#게시글 상세정보 조회
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'id'

#전체 게시글 조회 리스트 
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer

#특정 태그별 게시글 조회 리스트 
class ArticleByTagView(generics.ListAPIView):
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        tag_id = self.kwargs['tag_id']
        return Article.objects.filter(tags__id=tag_id)
    
