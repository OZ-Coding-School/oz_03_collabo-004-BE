from ai_hunsoos.models import AiHunsoo, Article
from ai_hunsoos.serializers import AiHunsooSerializer
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class AiHunsooDetailView(generics.RetrieveAPIView):
    """
    특정 게시글에 대한 AI 답변을 조회하는 뷰
    """

    queryset = AiHunsoo.objects.all()
    serializer_class = AiHunsooSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        # URL에서 article_id를 가져와 해당 Article에 대한 AiHunsoo 객체를 검색
        article_id = self.kwargs.get("article_id")
        try:
            # 특정 Article에 연결된 AiHunsoo 객체를 반환
            ai_hunsoo = AiHunsoo.objects.get(article_id=article_id)
            return ai_hunsoo
        except AiHunsoo.DoesNotExist:
            raise NotFound(detail="해당 게시글에 대한 AI 답변을 찾을 수 없습니다.")

    def get(self, request, *args, **kwargs):
        # AI 답변 조회 요청을 처리하고 결과 반환
        ai_hunsoo = self.get_object()
        serializer = self.get_serializer(ai_hunsoo)
        return Response(serializer.data)
