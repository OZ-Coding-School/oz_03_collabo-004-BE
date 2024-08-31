from elasticsearch_dsl import Search
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .search_indexes import ArticleDocument
from .serializers import ArticleSearchSerializer


class ArticleSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", None)
        if not query:
            return Response(
                {"error": "검색어를 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        search = Search(index=ArticleDocument.Index.name).query(
            "multi_match", query=query, fields=["title", "content"]
        )
        response = search.execute()

        results = [
            {"title": hit.title, "content": hit.content, "created_at": hit.created_at}
            for hit in response
        ]
        return Response(results)
