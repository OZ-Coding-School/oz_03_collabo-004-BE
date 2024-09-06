from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from notifications.models import Notification
from reports.models import ArticleReport, CommentReport


# 댓글이 작성될 때 알림
@receiver(post_save, sender=Comment)
def notify_user_on_comment(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.article.user,
            actor=instance.user,
            verb="comment",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            article=instance.article,
        )


# 게시글에 좋아요가 추가될 때 알림
@receiver(m2m_changed, sender=Article.likes.through)
def notify_user_on_like(sender, instance, action, **kwargs):
    if action == "post_add":
        for (
            user
        ) in (
            instance.likes.all()
        ):  # 여러 명의 사용자가 좋아요를 추가할 수 있으므로 반복문 사용
            Notification.objects.create(
                recipient=instance.user,
                actor=user,
                verb="like",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance,
            )


# 댓글이 채택될 때 알림
@receiver(post_save, sender=Comment)
def notify_user_on_comment_selection(sender, instance, **kwargs):
    if instance.is_selected:
        Notification.objects.create(
            recipient=instance.user,
            actor=instance.article.user,
            verb="select",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            article=instance.article,
        )


# AI 댓글이 생성될 때 알림
@receiver(post_save, sender=AiHunsoo)
def notify_user_on_ai_hunsoo(sender, instance, created, **kwargs):
    if not created and instance.status:
        Notification.objects.create(
            recipient=instance.article.user,
            actor=None,  # AI는 사용자 대신 자동으로 생성되므로 actor가 없을 수 있음
            verb="ai_response",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            article=instance.article,
        )


# 게시글 신고가 접수될 때 알림
@receiver(post_save, sender=ArticleReport)
def notify_admin_on_article_report(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            actor=instance.reported_user,
            verb="report",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            article=instance.reported_article,
            is_common=True,
        )


# 댓글 신고가 접수될 때 알림
@receiver(post_save, sender=CommentReport)
def notify_admin_on_comment_report(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            actor=instance.reported_user,
            verb="report",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            article=instance.reported_comment.article,
            is_common=True,
        )
