import sendgrid
from decouple import config
from django.contrib.sites.shortcuts import get_current_site
from authors.apps.authentication.backends import JWTAuthentication
from sendgrid.helpers.mail import(
    Email,
    Mail,
    Content
)
from rest_framework import (
    exceptions,
    generics,
    status,
    serializers
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny
)
from pyisemail import is_email
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Article,
    Reaction,
    Impression,
    Tag,
    Comment
)
from authors.apps.authentication.backends import JWTAuthentication
from authors.apps.profiles.serializers import ProfileListSerializer
from authors.apps.articles.exceptions import NotFoundException

from .renderers import (
    ArticleJSONRenderer,
    ReactionJSONRenderer,
    CommentJSONRenderer,
    ThreadJSONRenderer
)
from .serializers import (
    ArticleSerializer,
    ReactionSerializer,
    TagSerializer,
    CommentSerializer,
    ShareArticleSerializer
)


class ReturnArticle(APIView):
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        articles = Article.objects.filter(author_id=request.user.id)
        serializer = self.serializer_class(articles, many=True)
        return Response({'article': serializer.data}, status=status.HTTP_200_OK)    


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
        profile_serializer = ProfileListSerializer(profile)

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
                             "reading_time": serializer.data['reading_time'],
                             "comment_count": serializer.data['comment_count']
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


class CommentListCreateAPIView(generics.ListCreateAPIView):
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = Comment.objects.all()

    def post(self, request, slug):
        try:
            serializer_context = {
                'author': request.user.profile,
                'article': Article.objects.get(slug=slug)
            }
            serializer_data = request.data.get('comment', {})

            serializer = self.serializer_class(
                data=serializer_data,
                context=serializer_context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            comment = Comment()
            count = comment.get_count(slug=slug)
            new_count = count + 1
            Comment.comment_article(count=new_count, slug_param=slug)

        except Article.DoesNotExist:
            raise NotFoundException("The Article does not exist")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug, *args, **kwargs):
        comment = Comment.objects.select_related('article').filter(
            article__slug=slug
        )
        main_comment = comment.filter(parent=None).order_by('id')

        serializer = self.serializer_class(main_comment, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def update(self, request, slug, id, *args, **kwargs):
        try:
            serializer_context = {
                'author': request.user.profile,
                'id': Comment.objects.get(id=id)
            }
            serializer_data = request.data.get('comment', {})

            serializer = self.serializer_class(
                data=serializer_data,
                context=serializer_context,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.update(serializer_context["id"], serializer_data)
        except Comment.DoesNotExist:
            raise NotFoundException("The comment does not exist")

        return Response(
            {"updated_body": serializer.data["body"]},
            status=status.HTTP_200_OK
        )

    def destroy(self, instance, slug, id):
        try:
            comment = Comment.objects.get(id=id)
            comment_count = Comment()

            count = comment_count.get_count(slug=slug)
            new_count = count - 1
            Comment.comment_article(count=new_count, slug_param=slug)

            if comment.parent is not None:
                thread_count = comment_count.get_thread_count_delete(id=id)
                new_thread_count = thread_count - 1
                if new_thread_count < 0:
                    new_thread_count = 0
                Comment.thread_comment_delete(count=new_thread_count, id_param=id)
            comment.delete()
        except Article.DoesNotExist:
            raise NotFoundException("The Article does not exist")
        except Comment.DoesNotExist:
            raise NotFoundException("The comment does not exist")

        return Response(
            {"message": "comment has been deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class ThreadListCreateAPIView(generics.ListCreateAPIView):
    renderer_classes = (ThreadJSONRenderer,)
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = Comment.objects.all()

    def post(self, request, slug, id):
        try:
            if Comment.objects.get(id=id).parent is not None:
                return Response(
                    {"message": "Parent comment is already a sub comment"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer_context = {
                'author': request.user.profile,
                'article': Article.objects.get(slug=slug),
                'parent': Comment.objects.get(id=id).id
            }
            serializer_data = request.data.get('comment', {})

            serializer = self.serializer_class(
                data=serializer_data,
                context=serializer_context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            comment = Comment()
            count = comment.get_count(slug=slug)
            new_count = count + 1
            Comment.comment_article(count=new_count, slug_param=slug)

            
            thread_count = comment.get_thread_count(id=id)
            new_thread_count = thread_count + 1
            Comment.thread_comment(count=new_thread_count, id_param=id)

        except Article.DoesNotExist:
            raise NotFoundException("The Article does not exist")
        except Comment.DoesNotExist:
            raise NotFoundException("The parent comment does not exist")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug, id, *args, **kwargs):
        comment = Comment.objects.select_related('article').filter(
            article__slug=slug
        )
        main_comment = comment.filter(parent=id).order_by('id')

        serializer = self.serializer_class(main_comment, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ShareArticle(APIView):
    """
    This class handles sharing an article
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ShareArticleSerializer

    def post(self, request):
        """
        This method shares an articles
        :param request: contains subject, content and recipient
        :return: message and status code 200
        """
        sender = request.user.get_username()
        begin_subject_with = request.user.username
        share_data = request.data.get('article', {})
        serializer = self.serializer_class(data=share_data)
        serializer.is_valid(raise_exception=True)
        host = str(get_current_site(request)) + '/api/articles/'

        if not is_email(share_data['share_with']):
            raise serializers.ValidationError({
                    'email': 'Enter a valid email address.'
                }
            )
        share_article(begin_subject_with,host, sender, share_data['share_with'],
                      content=share_data['content']
        )

        return Response({"message": "Article has been successfully shared"},
                        status=status.HTTP_200_OK
        )


def share_article(start_subject, host, sender, receiver_email, content):
    """
    This method formats how subject and content
    :param host: current host
    :param sender: senders email
    :param receiver_email: email address for the recipient
    :param content: the slug being shared
    :return:
    """
    subject = "{} shared an article with you via Authors Haven".format(start_subject)
    content = Content(
                        "text/plain",
                        "Hey there, \n {} "
                        "via Authors Haven service has shared an article with you. "
                        "Please click the link below to view the article."
                        "\nhttp://{}{}/".format(start_subject, host, content)
                    )
    response = send_mail(sender, receiver_email, subject, content)
    return response


def send_mail(sender_email, receiver_mail, mail_subject, content):
    """
    This method shares sends out the email using send grid.
    :param sender_email: enders email
    :param receiver_mail: receiver's email
    :param mail_subject: rmail subject
    :param content: body to be shared
    :return:
    """
    sg = sendgrid.SendGridAPIClient(apikey=config('SENDGRID_API_KEY'))
    from_email = Email(sender_email)
    to_email = Email(receiver_mail)
    subject = mail_subject

    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
