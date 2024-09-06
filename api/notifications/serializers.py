from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from reports.models import Report
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
    article_title = serializers.CharField(source="article.title", read_only=True)
    comment_content = serializers.SerializerMethodField()

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
            "article_title",
            "comment_content",
            "read",
            "timestamp",
        ]

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
            if obj.verb == "like":
                return f"{obj.actor.nickname}님이 회원님의 게시글을 좋아합니다"
        elif obj.content_type.model == "aihunsoo":
            if obj.verb == "ai_response":
                return f"회원님의 게시글에 AI 훈수가 답변을 남겼습니다"
        elif obj.content_type.model == "comment":
            if obj.verb == "comment":
                return f"{obj.actor.nickname}님이 회원님의 게시글에 댓글을 남겼습니다"
            elif obj.verb == "select":
                return f"회원님의 댓글이 채택되었습니다"
        return "Unknown notification"

    def get_comment_content(self, obj):
        """content_type이 comment일 경우에만 필요"""
        if obj.content_type.model == "comment":
            comment = Comment.objects.get(id=obj.object_id)
            return comment.content
        return "None"


class AdminNotificationSerializer(serializers.ModelSerializer):
    reported_user_nickname = serializers.CharField(
        source="actor.nickname", read_only=True
    )
    reported_user_username = serializers.CharField(
        source="actor.username", read_only=True
    )
    target_object = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    report_id = serializers.IntegerField(source="object.id", read_only=True)
    article_id = serializers.IntegerField(source="article.id", read_only=True)
    description = serializers.SerializerMethodField()
    article_title = serializers.CharField(source="article.title", read_only=True)
    comment_content = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "reported_user_nickname",
            "reported_user_username",
            "verb",
            "content_type",
            "article_id",
            "report_id",
            "description",
            "article_title",
            "comment_content",
            "read",
            "timestamp",
        ]

    def get_content_type(self, obj):
        if obj.content_type.model == "articlereport":
            return "article"
        elif obj.content_type.model == "commentreport":
            return "comment"
        return "unknown"

    def get_description(self, obj):
        """content_type에 따라 description을 생성"""
        if obj.content_type.model == "articlereport":
            return f"{obj.reported_user_nickname}님의 게시글이 신고 접수 되었습니다"
        elif obj.content_type.model == "commentreport":
            return f"{obj.reported_user_nickname}님의 댓글이 신고 접수 되었습니다"
        return "Unknown notification"

    def get_comment_content(self, obj):
        """content_type이 comment_report일 경우에만 필요"""
        if obj.content_type.model == "commentreport":
            report = Report.objects.get(id=obj.object_id)
            comment = Comment.objects.get(id=report.reported_comment)
            return comment.content
        return "None"
