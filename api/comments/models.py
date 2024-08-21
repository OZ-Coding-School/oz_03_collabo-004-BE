from articles.models import Article
from common.models import TimeStampModel
from django.db import models
from users.models import User


class Comment(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    articles = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    content = models.TextField(null=False)
    is_selected = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "article")


class CommentImage(TimeStampModel):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=False)
    image_url = models.CharField(max_length=255, null=False)
    is_thumbnail = models.BooleanField(default=False)
