from ai_hunsoos.models import AiHunsoo
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Article


@receiver(post_save, sender=Article)
def create_initial_ai_hunsoo(sender, instance, created, **kwargs):
    if created:
        # 게시글 생성 시 초기 AI 응답 생성 (content는 null, status는 False)
        AiHunsoo.objects.create(article=instance, content=None, status=False)
