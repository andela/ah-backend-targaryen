from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """Create a new article"""

    class Meta:
        model = Article
        fields = [
            'author', 'title', 'description', 'body',
            'createdAt', 'updatedAt', 'slug'
        ]

    def create(self, validated_data):
        author = self.context.get('author', None)
        return Article.objects.create(author=author, **validated_data)
