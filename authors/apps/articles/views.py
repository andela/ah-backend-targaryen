from authors.apps.authentication.backends import JWTAuthentication
from rest_framework import (
    exceptions,
    generics,
    status
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Article,
    Reaction,
    Impression,
    Tag
)
from authors.apps.authentication.backends import JWTAuthentication
from authors.apps.profiles.serializers import ProfileSerializer

from .renderers import (
    ArticleJSONRenderer,
    ReactionJSONRenderer
)
from .serializers import (
    ArticleSerializer,
    ReactionSerializer,
    TagSerializer
)


class CreateArticle(generics.CreateAPIView):
    """Class for creation of an article"""

    serializer_class = ArticleSerializer
    renderer_class = (ArticleJSONRenderer,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def create(self, request):
        serializer_context = {'author': request.user.profile}
        serializer_data = request.data.get('article', {})

        time_to_read = Article.article_reading_time(serializer_data['body'])
        serializer_data['readingTime'] = time_to_read
        serializer = self.serializer_class(data=serializer_data,
                                           context=serializer_context)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"article": serializer.data}, status=status.HTTP_201_CREATED)


class ArticleRetrieveUpdate(APIView):
    """Class to get, update or delete an article"""

    serializer_class = ArticleSerializer
    renderer_class = (ArticleJSONRenderer,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, slug):
        """Get a single article
        :params request request slug
        :return article"""

        article = Article.get_article(slug=slug)
        serializer = self.serializer_class(article)

        profile = Article.get_profile(serializer.data['author'])
        profile_serializer = ProfileSerializer(profile)

        return Response(
                {"article": {
                             "author": profile_serializer.data,
                             "title": serializer.data['title'],
                             "description": serializer.data['description'],
                             "body": serializer.data['body'],
                             "createdAt": serializer.data['createdAt'],
                             "updatedAt": serializer.data['updatedAt'],
                             "slug": serializer.data['slug'],
                             "fav_count": serializer.data['favourite_count'],
                             "likes": serializer.data['likes'],
                             "dislikes": serializer.data['dislikes'],
                             "tagList": serializer.data['tagList'],
                             "reading_time": serializer.data['reading_time']
                            },
                 "message": "Success"
                 },
                status=status.HTTP_200_OK
        )

    def put(self, request, slug):
        """Update a single article
        :params request slug
        :return article"""

        article = Article.get_user_article(user_email=request.user, slug=slug)
        serializer = self.serializer_class(article, data=request.data['article'])
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"article": serializer.data,
             "message": "Article successfully updated"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, slug):
        """Delete a single article
        :params request slug
        :return article"""
        Article.delete_article(user_email=request.user, slug=slug)

        return Response(
            {"message": "Article has been deleted"},
            status=status.HTTP_204_NO_CONTENT
        )


class ArticleList(generics.ListAPIView):

    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = Article.objects.all()
        return queryset


class TagList(generics.ListAPIView):
    """Class to get a list of existing tags"""

    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)
        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)
        

class ReactionView(APIView):
    """Class to like or dislike an article"""

    serializer_class = ReactionSerializer
    renderer_class = (ReactionJSONRenderer,)
    permission_classes = (IsAuthenticated,)

    def check_reaction(self, reaction_data, request):

        like_verb = 'liked'
        dislike_verb = 'disliked'
        fav_verb = 'added'
        to_from = 'to'
        message = dict()
        if request.method == 'DELETE':
            like_verb = 'unliked'
            dislike_verb = 'removed the dislike from'
            fav_verb = 'removed'
            to_from = 'from'

        if reaction_data == 'Like':
            message = {
                'Message': 'You have {} this article'.format(like_verb)
            }
        elif reaction_data == 'Dislike':
            message = {
                'Message': 'You have {} this article'.format(dislike_verb)
            }
        elif reaction_data == 'Favourite':
            message = {
                'Message':
                'You have {0} this article {1} your favourites'.format(
                    fav_verb, to_from
                )
            }
        return message

    def check_validation(self, slug, request):
        username = request.user.username
        article = Article.get_article(slug=slug)
        impression = Impression.objects.get(name=request.data.get('reaction'))
        serializer_data = {}
        serializer_context = {
            'user': request.user,
            'article': article,
            'reaction': Impression.objects.get(
                name=request.data.get('reaction')
                ),
            }
        serializer_data['reaction'] = impression.id
        serializer_data['user'] = request.user.id
        serializer_data['article'] = article.id
        serializer = self.serializer_class(
            data=serializer_data, context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        return serializer

    def post(self, request, slug):
        serializer = self.check_validation(slug, request)
        message = self.check_reaction(
            request.data.get('reaction'),
            request
        )

        serializer.save()

        return Response(
            message,
            status=status.HTTP_200_OK
        )

    def delete(self, request, slug):

        try:
            article = Article.get_article(slug=slug)
            reaction= Impression.objects.get(
                name=request.data['reaction']
            )
            reaction = Reaction.objects.get(
                article=article.id,
                user=request.user.id,
                reaction=reaction
            )
            message = self.check_reaction(
                request.data['reaction'],
                request
            )
            ReactionSerializer.reaction_value(
                reaction.id, article.slug, article, -1
            )
            reaction.delete()
            return Response(message, status=status.HTTP_204_NO_CONTENT)

        except Reaction.DoesNotExist:
            message = 'You have not yet interacted with this article'
            raise exceptions.ParseError(message)
