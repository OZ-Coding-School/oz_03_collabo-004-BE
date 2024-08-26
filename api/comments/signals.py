from ai_hunsoos.models import AiHunsoo
from ai_hunsoos.utils import generate_ai_response
from articles.models import Article
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Comment


@receiver(post_save, sender=Comment)
def create_ai_hunsoo(sender, instance, created, **kwargs):
    # 댓글이 업데이트되었고 is_selected가 True로 변경된 경우
    if not created and instance.is_selected:
        # 관련된 게시글
        article = instance.article

        # AI 응답 생성
        ai_response = generate_ai_response(article.content, instance.content)

        # AiHunsoo 테이블에 저장
        AiHunsoo.objects.create(article=article, content=ai_response)
