from articles.models import Article
from articles.serializers import ArticleListSerializer
from elasticsearch_dsl import Search
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .search_indexes import ArticleDocument


class ArticleSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", None)
        if not query:
            return Response(
                {"error": "검색어를 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Elasticsearch에서 검색
        search = Search(index=ArticleDocument.Index.name).query(
            "multi_match", query=query, fields=["title", "content"]
        )
        response = search.execute()

        # Elasticsearch에서 반환된 결과의 ID를 가져옴
        article_ids = [hit.meta.id for hit in response]

        # Django ORM을 통해 Article 객체를 가져옴
        articles = Article.objects.filter(id__in=article_ids)

        # ArticleListSerializer를 사용하여 직렬화
        serializer = ArticleListSerializer(
            articles, many=True, context={"request": request}
        )

        return Response(serializer.data)
