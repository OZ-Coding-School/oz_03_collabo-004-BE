from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from tags.models import Tag

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)
    selected_tags = models.ManyToManyField("tags.Tag", blank=True)
    warning_count = models.IntegerField(default=0)
    hunsoo_level = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username
