from ai_hunsoos.models import AiHunsoo
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Article


@receiver(post_save, sender=Article)
def create_initial_ai_hunsoo(sender, instance, created, **kwargs):
    if created:
        # 게시글 생성 시 초기 AI 응답 생성 (content는 null, status는 False)
        AiHunsoo.objects.create(article=instance, content=None, status=False)


# 게시글 생성, 수정, 삭제시 캐시 무효화
@receiver([post_save, post_delete], sender=Article)
def article_changed_handler(sender, instance, **kwargs):
    """
    게시글 생성, 수정, 삭제 시 캐시 무효화.
    """
    # 여러 페이지에 대해 캐시 키를 삭제
    for page_num in range(1, 100):  # 페이지 수에 따라 적절한 범위 지정
        cache_key = f"article_list_page_{page_num}"
        cache.delete(cache_key)
