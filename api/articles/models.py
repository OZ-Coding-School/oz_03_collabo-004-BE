from common.models import TimeStampModel
from django.conf import settings
from django.db import models
from tags.models import Tag
from users.models import User


class Article(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    content = models.TextField(null=False)
    is_closed = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    #hunsoo_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class ArticleImage(TimeStampModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    image = models.ImageField(upload_to="articles/", null=False)
    is_thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.article.title} - {self.id}"
