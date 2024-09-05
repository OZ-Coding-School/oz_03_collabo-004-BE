from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_nickname = serializers.CharField(source="actor.nickname", read_only=True)
    actor_username = serializers.CharField(source="actor.username", read_only=True)
    target_object = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    object_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "actor_nickname",
            "actor_username",
            "verb",
            "content_type",
            "object_id",
            "target_object",
            "read",
            "timestamp",
        ]

    def get_target_object(self, obj):
        if isinstance(obj.target, Comment):
            return f"Comment by {obj.actor.nickname} on {obj.target.article.title}"
        elif isinstance(obj.target, Article):
            return f"Article: {obj.target.title}"
        elif isinstance(obj.target, AiHunsoo):
            return f"AI Hunsoo Response to {obj.target.article.title}"
        else:
            return "Unknown target"

    def get_content_type(self, obj):
        """알림 대상 객체의 타입(article, comment)을 반환"""
        if obj.content_type.model == "comment":
            return "comment"
        elif obj.content_type.model == "article":
            return "article"
        elif obj.content_type.model == "aihunsoo":
            return "ai_hunsoo"
        return "unknown"
