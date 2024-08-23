from articles.models import Article
from common.models import TimeStampModel
from django.db import models
from users.models import User


class Comment(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=False, related_name="comments"
    )
    content = models.TextField(null=False)
    is_selected = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)  # 도움이 돼요 수
    not_helpful_count = models.IntegerField(default=0)  # 안돼요 수

    class Meta:
        unique_together = ("user", "article")

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"


class CommentImage(TimeStampModel):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=False, related_name="images"
    )
    image = models.ImageField(upload_to="comments/", null=True, blank=True)

    def __str__(self):
        return f"{self.comment.id} - {self.id} - {self.image.name}"


class CommentReaction(TimeStampModel):
    REACTION_CHOICES = (
        ("helpful", "Helpful"),
        ("not_helpful", "Not Helpful"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=False, related_name="reactions"
    )
    reaction_type = models.CharField(max_length=12, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ("user", "comment")

    def __str__(self):
        return f"{self.user.username} - {self.comment.id} - {self.reaction_type}"
