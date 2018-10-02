from django.db import models

class TimeStampedModel(models.Model):
    """creates a timestamps in the models that inherit it"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at', 'updated_at']
