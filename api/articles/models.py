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
    likes = models.ManyToManyField(User, related_name="liked_articles", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    # 좋아요 집계 동적 실시간 반영
    @property
    def like_count(self):
        return self.likes.count()


class ArticleImage(TimeStampModel):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, related_name="images"
    )
    image = models.URLField(max_length=500, null=False)  # S3 URL을 직접 저장
    is_thumbnail = models.BooleanField(default=False)
    is_temporary = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.article.title} - {self.id}"

    @property
    def image_url(self):
        return self.image if self.image else None  # 이미지를 반환할 때는 S3 URL 반환
