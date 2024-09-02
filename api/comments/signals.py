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

        # 해당 게시글에 대한 AI 댓글이 이미 존재하고 status가 True인 경우
        try:
            ai_hunsoo = AiHunsoo.objects.get(article=article, status=True)
            # 이미 존재하므로 업데이트하지 않음
            return
        except AiHunsoo.DoesNotExist:
            # AI 댓글이 존재하지 않거나 status가 False인 경우
            pass

        # AI 응답 생성
        ai_response = generate_ai_response(article.content, instance.content)

        # AiHunsoo 테이블에 저장하거나 업데이트
        ai_hunsoo, created = AiHunsoo.objects.get_or_create(
            article=article, defaults={"content": ai_response, "status": True}
        )
        if not created:
            # 이미 존재하는 경우 업데이트
            ai_hunsoo.content = ai_response
            ai_hunsoo.status = True
            ai_hunsoo.save()
