from articles.models import Article
from comments.models import Comment
from common.models import TimeStampModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ArticleReport(TimeStampModel):
    class ReportStatus(models.TextChoices):
        PENDING = "PD", "대기 중"
        IN_PROGRESS = "IP", "처리 중"
        RESOLVED = "RS", "처리 완료"
        REJECTED = "RJ", "거부됨"

    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_articles", null=False
    )
    reported_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_against_user", null=False
    )
    reported_article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    report_detail = models.CharField(max_length=255, null=False)
    status = models.CharField(
        max_length=2,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
    )

    def __str__(self):
        return f"{self.id}-{self.status}"


class CommentReport(TimeStampModel):
    class ReportStatus(models.TextChoices):
        PENDING = "PD", "대기 중"
        IN_PROGRESS = "IP", "처리 중"
        RESOLVED = "RS", "처리 완료"
        REJECTED = "RJ", "거부됨"

    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_comments", null=False
    )
    reported_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments_against_user", null=False
    )
    reported_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=False)
    report_detail = models.CharField(max_length=255, null=False)
    status = models.CharField(
        max_length=2,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
    )

    def __str__(self):
        return f"{self.id}-{self.status}"
