from rest_framework.permissions import AllowAny
from rest_framework import generics

from .models import Tag
from .serializers import TagSerializer


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny] 
