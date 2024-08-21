from common.models import TimeStampModel
from django.db import models
from users.models import User


class Article(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    content = models.TextField(null=False)
    is_closed = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)


class ArticleImage(TimeStampModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    image_url = models.CharField(max_length=255, null=False)
    is_thumbnail = models.BooleanField(default=False)
