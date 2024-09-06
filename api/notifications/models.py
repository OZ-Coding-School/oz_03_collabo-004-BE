from ai_hunsoos.models import AiHunsoo
from articles.models import Article
from comments.models import Comment
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()

NOTIFICATION_TYPES = (
    ("comment", "Commented on your post"),
    ("like", "Liked your post"),
    ("select", "Selected your comment"),
    ("ai_response", "AI responded to your post"),
    ("report", "A report has been received"),
)


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    actor = models.ForeignKey(
        User, related_name="actor", on_delete=models.CASCADE, null=True, blank=True
    )
    verb = models.CharField(max_length=255, choices=NOTIFICATION_TYPES)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    # 어드민 알림은 recipient null로 하고 is_admin=True
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        if self.is_common:
            return f"Common Notification - {self.get_verb_display()}"
        return f"Notification for {self.recipient.username} - {self.get_verb_display()}"
