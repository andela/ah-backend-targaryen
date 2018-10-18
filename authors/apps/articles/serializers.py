from rest_framework import exceptions, serializers

from .models import Article, Impression, Reaction, Tag
from .relations import TagRelatedField


class ArticleSerializer(serializers.ModelSerializer):
    """Create a new article"""

    tagList = TagRelatedField(many=True, required=False, queryset=Tag.objects.all(), source='tags')

    class Meta:
        model = Article
        fields = [
            'author', 'title', 'description', 'body',
            'createdAt', 'updatedAt', 'slug', 'favourite_count',
            'likes', 'dislikes', 'tagList', 'reading_time'
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
        return Article.objects.create(author=author, **validated_data)


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['article', 'user', 'reaction']

    @staticmethod
    def reaction_value(reaction, article_slug, article, reaction_integer):
        react_id = 0

        if reaction == Impression.objects.get(name='Like').id:
            react_id = 1
            updated_likes = article.likes + reaction_integer
            Article.objects.filter(slug=article_slug).update(
                likes=updated_likes
            )
        elif reaction == Impression.objects.get(name='Dislike').id:
            react_id = 2
            updated_dislikes = article.dislikes + reaction_integer
            Article.objects.filter(slug=article_slug).update(
                dislikes=updated_dislikes
            )
        elif reaction == Impression.objects.get(name='Favourite').id:
            react_id = 3
            updated_favourites = article.favourite_count + reaction_integer
            Article.objects.filter(slug=article_slug).update(
                favourite_count=updated_favourites
            )
        else:
            message = 'You have entered invalid data.'
            raise exceptions.PermissionDenied(message)
        return react_id

    def validate(self, data):
        try:
            current_reaction = Reaction.objects.get(
                article=data.get('article'),
                user=data.get('user'),
                reaction=data.get('reaction')
            )
            if isinstance(current_reaction, object):
                message = 'You have already {}d this article.'.format(
                    data.get('reaction').name
                )
                raise exceptions.ParseError(message)
        except Reaction.DoesNotExist:
            article = data.get('article')
            reaction = data.get('reaction').id
            react_id = ReactionSerializer.reaction_value(
                reaction, article.slug, article, 1
            )
            if reaction == Impression.objects.get(name='Like').id:
                react_id = 1
                updated_likes = article.likes + 1
                Article.objects.filter(slug=article.slug).update(
                    likes=updated_likes
                )
            elif reaction == Impression.objects.get(name='Dislike').id:
                react_id = 2
                updated_dislikes = article.dislikes + 1
                Article.objects.filter(slug=article.slug).update(
                    dislikes=updated_dislikes
                )
            elif reaction == Impression.objects.get(name='Favourite').id:
                react_id = 3
                updated_favourites = article.favourite_count + 1
                Article.objects.filter(slug=article.slug).update(
                    favourite_count=updated_favourites
                )
            else:
                message = 'You have entered invalid data.'
                raise exceptions.PermissionDenied(message)
            return {
                'article': data.get('article'),
                'reaction': react_id,
                'user': data.get('user')
            }

    def create(self, validated_data):
        user = self.context.get('user', None)
        article = self.context.get('article', None)
        reaction = self.context.get('reaction', None)
        return Reaction.objects.create(
            user=user, article=article, reaction=reaction
        )
