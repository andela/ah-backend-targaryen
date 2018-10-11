from django.db import models
from rest_framework import exceptions
from django.utils.text import slugify

from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User


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
        