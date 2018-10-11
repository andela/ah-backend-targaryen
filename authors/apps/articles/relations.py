from rest_framework import serializers

from .models import Tag

class TagRelatedField(serializers.RelatedField):
    """Class for Tag RelatedField"""

    def to_internal_value(self, data):
        """To implement a read-write relational field"""
        tag, created = Tag.objects.get_or_create(tag=data)
        return tag

    def to_representation(self, value):
        """Override the RelationField """
        return value.tag
