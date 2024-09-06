from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
