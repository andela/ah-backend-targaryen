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
    reading_stats = models.CharField(max_length=100, default='0 minutes')

    def __str__(self):
        self.user.username

    @staticmethod
    def increment_read_stats(current_reading_stats, int_reading_time):
        """ 
        Increment the user's reading stats 
        by the reading time of the article they have fetched
        """

        integers_found = [int(current_reading_stats)
                    for current_reading_stats in
                    str.split(current_reading_stats)
                    if current_reading_stats.isdigit()]
        cur_reading_stats = integers_found[0]
        read_stats = cur_reading_stats + int_reading_time
        if read_stats == 1:
            return '1 minute'
        else:
            return str(int(read_stats)) + ' minutes'
