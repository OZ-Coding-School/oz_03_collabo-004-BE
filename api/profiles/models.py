from common.models import TimeStampModel
from django.db import models
from users.models import User


class Profile(TimeStampModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    bio = models.TextField()
    hunsoo_level = models.PositiveIntegerField(default=1)
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    selectd_comment_count = models.PositiveIntegerField(default=0)
