from rest_framework import serializers

from .search_indexes import ArticleDocument


class ArticleSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleDocument
        fields = ["title", "content", "created"]
