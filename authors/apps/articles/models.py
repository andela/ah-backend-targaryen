from django.db import models
from rest_framework import exceptions
from django.utils.text import slugify

from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStampedModel


class Article(models.Model):
    """Model for an article"""

    author = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE,
                               null=True)
    slug = models.SlugField(max_length=140, unique=True, null=True)
    title = models.CharField(max_length=150, null=True)
    description = models.CharField(max_length=255, null=True)
    body = models.TextField(null=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)
    tags = models.ManyToManyField(
        'articles.Tag', related_name='articles'
    )
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    favourite_count = models.PositiveIntegerField(default=0)
    reading_time = models.CharField(max_length=100, null=True)
    comment_count = models.PositiveIntegerField(default=0)

    @staticmethod
    def get_article(slug):
        """Method to query db for article
        :params slug
        :return article"""
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            message = "No article was found"
            raise exceptions.NotFound(message)
        return article

    @staticmethod
    def delete_article(user_email, slug):
        """Method to delete article from db
        :params slug
        :return """
        user = User.objects.get(email=user_email)
        user_id = user.id
        try:
            article = Article.objects.get(author_id=user_id, slug=slug)
        except Article.DoesNotExist:
            message = "You are not authenticated for the action"
            raise exceptions.PermissionDenied(message)
        return article.delete()

    @staticmethod
    def article_reading_time(body):
        new_line_words = body.split('\n')

        total_words = 0
        for group in new_line_words:
            total_words += len(group.split())

        # Assume a reading time of 275WPM
        time_to_read = (total_words/275)
        if time_to_read < 1:
            return 'Less than a minute'
        elif time_to_read < 2:
            return 'About 1 minute'

        # Return a value rounded up or down if below or above 5
        return str(int(round(time_to_read))) + ' minutes'

    @staticmethod
    def get_reading_time_as_integer(reading_time):
        """ Extract reading time as integer """

        int_reading_time = 0
        if reading_time == 'Less than a minute':
            int_reading_time = 1
        elif reading_time == 'About 1 minute':
            int_reading_time = 2
        else:
            integers_found = [int(reading_time)
                    for reading_time in str.split(reading_time)
                    if reading_time.isdigit()]
            int_reading_time = integers_found[0]
        return int_reading_time

    @staticmethod
    def get_profile(profile_id):
        return Profile.objects.get(id=profile_id)

    @staticmethod
    def get_user_article(user_email, slug):
        user = User.objects.get(email=user_email)
        user_id = user.id
        try:
            article = Article.objects.get(author_id=user_id, slug=slug)
        except Article.DoesNotExist:
            message = "You are not authenticated for the action"
            raise exceptions.PermissionDenied(message)
        return article

    def __str__(self):
        return self.title

    def _get_unique_slug(self):
        slug = slugify(self.title)
        number = 1
        while Article.objects.filter(slug=slug).exists():
            slug = '{}-{}'.format(slug, number)
            number += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Model for tags """

    tag = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.tag
   


class Impression(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    image = models.URLField(blank=True)


class Reaction(models.Model):
    '''
    This model stores the likes,
    dislikes and favourites that users add to articles
    '''
    article = models.ForeignKey(
        Article, models.SET_NULL, blank=False, null=True,
    )
    user = models.ForeignKey(
        User, models.SET_NULL, blank=False, null=True,
    )
    reaction = models.ForeignKey(
        Impression, models.SET_NULL, blank=False, null=True,
    )

    def __int__(self):
        return self.article_id


class Comment(TimeStampedModel):
    """Model for comments on articles"""
    body = models.TextField(null=True)
    author = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        null=True
    )
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.CASCADE,
        null=True
    )
    parent = models.TextField(null=True, blank=True)
    thread_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.body

    @staticmethod
    def comment_article(count, slug_param):
        article = Article.get_article(slug=slug_param)
        article.__dict__.update(comment_count=count)
        article.save()

    def get_count(self, slug):
        self.slug = slug
        article = Article.objects.get(slug=self.slug)
        return article.comment_count
    
    @staticmethod
    def thread_comment(count, id_param):
        comment = Comment.objects.get(id=id_param)
        comment.__dict__.update(thread_count=count)
        comment.save()
    
    def get_thread_count(self, id):
        self.id = id
        comment = Comment.objects.get(id=self.id)
        return comment.thread_count
    
    @staticmethod
    def thread_comment_delete(count, id_param):
        comment = Comment.objects.get(id=id_param)
        parent_comment = Comment.objects.get(id=comment.parent)
        parent_comment.__dict__.update(thread_count=count)
        parent_comment.save()
    
    def get_thread_count_delete(self, id):
        self.id = id
        comment = Comment.objects.get(id=self.id)
        parent_comment = Comment.objects.get(id=comment.parent)
        # import pdb; pdb.set_trace()
        return parent_comment.thread_count
