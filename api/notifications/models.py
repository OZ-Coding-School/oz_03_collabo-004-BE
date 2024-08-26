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
)


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    actor = models.ForeignKey(
        User, related_name="actor", on_delete=models.CASCADE, null=True, blank=True
    )
    verb = models.CharField(max_length=255, choices=NOTIFICATION_TYPES)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.get_verb_display()}"
