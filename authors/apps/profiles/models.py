from django.db import models

from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStampedModel


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    following = models.ManyToManyField(
        'self', related_name='followers', symmetrical=False
    )

    def __str__(self):
        self.user.username
    
    def follow(self, profile):
        self.following.add(profile)
    
    def unfollow(self, profile):
        self.following.remove(profile)
    
    def is_following(self, profile):
        return self.following.filter(pk=profile.pk).exists()
