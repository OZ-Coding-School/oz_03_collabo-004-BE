from articles.models import Article
from common.models import TimeStampModel
from django.db import models


class AiHunsoo(TimeStampModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    content = models.TextField(null=True)
    status = models.BooleanField(default=False)
