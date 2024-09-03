from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..models import Article
from ..serializers import ArticleListSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def article_search_view(request):
    query = request.GET.get("q")
    results = []
    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()

    serializer = ArticleListSerializer(results, many=True)
    return Response(serializer.data)
