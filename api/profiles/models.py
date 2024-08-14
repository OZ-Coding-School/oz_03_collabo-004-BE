from common.models import TimeStampedModel
from django.db import models
from users.models import User


class Profile(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    bio = models.TextField()
    hunsoo_level = models.PositiveIntegerField(default=1)
    profile_image = models.ForeignKey(
        "profiles.ProfileImage", null=True, blank=True, on_delete=models.SET_NULL
    )
    selectd_comment_count = models.PositiveIntegerField(default=0)


class ProfileImage(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    image_url = models.CharField(max_length=255, null=False)
    is_active = models.BooleanField(default=True)
