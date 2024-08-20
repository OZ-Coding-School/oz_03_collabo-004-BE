from rest_framework import serializers
from .models import Tag, Question

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_id', 'name']