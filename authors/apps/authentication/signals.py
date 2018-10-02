from django.dispatch import receiver
from django.db.models.signals import post_save

from authors.apps.profiles.models import Profile
from .models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, *args, **kwargs):
    """
    Mehtod to create a profile when a user is created
    When a user is updated, the signal will run but the created condition
    will not pass. Therefore a profile is only created when
    a user registers.
    """
    if instance and created:
        instance.profile = Profile.objects.create(user=instance)
