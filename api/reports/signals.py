from django.db.models.signals import post_save
from django.dispatch import receiver
from profiles.models import Profile

from .models import ArticleReport, CommentReport


@receiver(post_save, sender=ArticleReport)
def update_warning_article(sender, instance, created, **kwargs):
    # article_report가 업데이트되었고 status가 RS(resolved)로 변경된 경우
    if not created and instance.status == "RS":
        # 신고된 유저
        reported_user = instance.reported_user

        # Profile 객체를 가져오고 warning_count 증가
        try:
            profile = Profile.objects.get(user=reported_user)
            profile.warning_count += 1
            profile.save()
        except Profile.DoesNotExist:
            # Profile이 없는 경우 처리 (optional)
            print(f"No profile found for user {reported_user.id}")


@receiver(post_save, sender=CommentReport)
def update_warning_comment(sender, instance, created, **kwargs):
    # comment_report가 업데이트되었고 status가 RS(resolved)로 변경된 경우
    if not created and instance.status == "RS":
        # 신고된 유저
        reported_user = instance.reported_user

        # Profile 객체를 가져오고 warning_count 증가
        try:
            profile = Profile.objects.get(user=reported_user)
            profile.warning_count += 1
            profile.save()
        except Profile.DoesNotExist:
            # Profile이 없는 경우 처리 (optional)
            print(f"No profile found for user {reported_user.id}")
