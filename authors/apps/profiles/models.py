from django.db import models

from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStampedModel


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)

    def __str__(self):
        self.user.username
