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
    article_id = serializers.IntegerField(source="article.id", read_only=True)
    description = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "actor_nickname",
            "actor_username",
            "verb",
            "content_type",
            "article_id",
            "object_id",
            "description",
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

    def get_description(self, obj):
        """content_type과 verb에 따라 description을 생성"""
        if obj.content_type.model == "article":
            if obj.verb == "comment":
                return f"{obj.actor.nickname}님이 회원님의 게시글에 댓글을 남겼습니다: {obj.article.title}"
            elif obj.verb == "like":
                return f"{obj.actor.nickname}님이 회원님의 게시글을 좋아합니다: {obj.article.title}"
            elif obj.verb == "ai_hunsoo":
                return f"회원님의 게시글에 AI 훈수가 답변을 남겼습니다: {obj.article.title}"
        elif obj.content_type.model == "comment" and obj.verb == "select":
            comment = Comment.objects.get(id=obj.object_id)
            return f"회원님의 댓글이 채택되었습니다: {comment.content}"
        return "Unknown notification"
