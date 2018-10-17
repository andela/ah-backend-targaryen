from rest_framework import serializers

from .models import (
    Article,
    Tag
)
from .relations import TagRelatedField


class ArticleSerializer(serializers.ModelSerializer):
    """Create a new article"""

    tagList = TagRelatedField(many=True, required=False, queryset=Tag.objects.all(), source='tags')

    class Meta:
        model = Article
        fields = [
            'author', 'title', 'description', 'body',
            'createdAt', 'updatedAt', 'slug', 'tagList'
        ]

    def create(self, validated_data):
        author = self.context.get('author', None)
        tags_data = validated_data.pop('tags', [])
        article = Article.objects.create(author=author, **validated_data)
        for tag in tags_data:
            article.tags.add(tag)
        return article


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, value):
        return value.tag
