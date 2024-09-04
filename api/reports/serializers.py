from rest_framework import serializers

from .models import ArticleReport, CommentReport


class ArticleReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReport
        fields = [
            "id",
            "reporter",
            "reported_user",
            "reported_article",
            "report_detail",
            "status",
        ]


class CommentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReport
        fields = [
            "id",
            "reporter",
            "reported_user",
            "reported_comment",
            "report_detail",
            "status",
        ]


class ArticleReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReport
        fields = ["status"]


class CommentReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReport
        fields = ["status"]


class ArticleReportAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReport
        fields = "__all__"


class CommentReportAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReport
        fields = "__all__"


class UserReportStatusSerializer(serializers.Serializer):
    article_reports = ArticleReportAllSerializer(many=True)
    comment_reports = CommentReportAllSerializer(many=True)


class ReportStatusSerializer(serializers.Serializer):
    article_reports = ArticleReportAllSerializer(many=True)
    comment_reports = CommentReportAllSerializer(many=True)
