from authors.apps.authentication.backends import JWTAuthentication
from rest_framework import generics, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Article,
    Tag
)
from authors.apps.profiles.serializers import ProfileSerializer
from .renderers import ArticleJSONRenderer
from .serializers import (
    ArticleSerializer,
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
                             "tagList": serializer.data['tagList'],
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
    permission_classes = (AllowAny,)

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
        