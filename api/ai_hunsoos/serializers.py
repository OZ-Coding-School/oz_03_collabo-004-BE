from ai_hunsoos.models import AiHunsoo
from rest_framework import serializers


class AiHunsooSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiHunsoo
        fields = ["status", "article", "content", "created_at", "updated_at"]
