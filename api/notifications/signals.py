from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from notifications.models import Notification
from reports.models import ArticleReport, CommentReport


# 댓글이 작성될 때 알림
@receiver(post_save, sender=Comment)
def notify_user_on_comment(sender, instance, created, **kwargs):
    if created:
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            recipient=instance.article.user,
            actor=instance.user,
            verb="comment",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
        ).exists():
            # 중복 알림이 없다면 새 알림 생성
            Notification.objects.create(
                recipient=instance.article.user,
                actor=instance.user,
                verb="comment",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance.article,
                is_admin=False,
            )


# 게시글에 좋아요가 추가될 때 알림
@receiver(m2m_changed, sender=Article.likes.through)
def notify_user_on_like(sender, instance, action, **kwargs):
    if action == "post_add":
        for user in instance.likes.all():
            Notification.objects.create(
                recipient=instance.user,
                actor=user,
                verb="like",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance,
                is_admin=False,
            )

    elif action == "post_remove":
        for user in kwargs.get("pk_set", []):  # 좋아요 취소한 사용자들
            Notification.objects.filter(
                recipient=instance.user,
                actor_id=user,  # user_id로 필터링
                verb="like",
                object_id=instance.id,
                content_type=ContentType.objects.get_for_model(instance),
            ).delete()


# 댓글이 채택될 때 알림
@receiver(post_save, sender=Comment)
def notify_user_on_comment_selection(sender, instance, **kwargs):
    if instance.is_selected:
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            recipient=instance.user,
            actor=instance.article.user,
            verb="select",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
        ).exists():
            # 중복 알림이 없다면 새 알림 생성
            transaction.on_commit(
                lambda: Notification.objects.create(
                    recipient=instance.user,
                    actor=instance.article.user,
                    verb="select",
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id,
                    article=instance.article,
                    is_admin=False,
                )
            )


# AI 댓글이 생성될 때 알림
@receiver(post_save, sender=AiHunsoo)
def notify_user_on_ai_hunsoo(sender, instance, created, **kwargs):
    if not created and instance.status:
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            recipient=instance.article.user,
            verb="ai_response",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
        ).exists():
            # 중복 알림이 없다면 새 알림 생성
            Notification.objects.create(
                recipient=instance.article.user,
                actor=None,  # AI는 사용자 대신 자동으로 생성되므로 actor가 없을 수 있음
                verb="ai_response",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance.article,
                is_admin=False,
            )


# 게시글 신고가 처리 완료되었을 때 알림
@receiver(post_save, sender=ArticleReport)
def update_warning_article(sender, instance, created, **kwargs):
    if not created and instance.status == "RS":
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            recipient=instance.reported_user,
            verb="report",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
        ).exists():
            Notification.objects.create(
                recipient=instance.reported_user,
                actor=instance.reported_user,
                verb="report",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance.reported_article,
                is_admin=False,
            )


# 댓글 신고가 처리 완료되었을 때 알림
@receiver(post_save, sender=CommentReport)
def update_warning_comment(sender, instance, created, **kwargs):
    if not created and instance.status == "RS":
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            recipient=instance.reported_user,
            verb="report",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
        ).exists():
            Notification.objects.create(
                recipient=instance.reported_user,
                actor=instance.reported_user,
                verb="report",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance.reported_comment.article,
                is_admin=False,
            )


# 게시글 신고가 접수될 때 알림
@receiver(post_save, sender=ArticleReport)
def notify_admin_on_article_report(sender, instance, created, **kwargs):
    if created:
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            actor=instance.reported_user,
            verb="report",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
            is_admin=True,
        ).exists():
            Notification.objects.create(
                actor=instance.reported_user,
                verb="report",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance.reported_article,
                is_admin=True,
            )


# 댓글 신고가 접수될 때 알림
@receiver(post_save, sender=CommentReport)
def notify_admin_on_comment_report(sender, instance, created, **kwargs):
    if created:
        # 동일한 알림이 이미 존재하는지 확인
        if not Notification.objects.filter(
            actor=instance.reported_user,
            verb="report",
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
            is_admin=True,
        ).exists():
            Notification.objects.create(
                actor=instance.reported_user,
                verb="report",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                article=instance.reported_comment.article,
                is_admin=True,
            )
