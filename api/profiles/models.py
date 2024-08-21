from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from tags.models import Tag
# added MyPage
from django.contrib.auth.models import User

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    selected_tags = models.ManyToManyField("tags.Tag", blank=True)
    warning_count = models.IntegerField(default=0)
    hunsoo_level = models.IntegerField(default=1)
    # added nickname field
    nickname = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return self.user.username
