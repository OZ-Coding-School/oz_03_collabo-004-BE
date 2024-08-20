from rest_framework import generics
from .models import Tag, Question
from .serializers import TagSerializer, QuestionSerializer

class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer