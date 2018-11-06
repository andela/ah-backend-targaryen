from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile

from .models import Article, Impression, Reaction


class ViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.username = "johndoe"
        self.email = "johndoe@gmail.com"
        self.password = "Password1"

        self.user_data = {
            "user": {
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
        }
        self.share_data = {
            "article": {
                "share_with": "kakaemma1@gmail.com",
                "content": "music-in-town"
            }
        }
        self.invalid_email = {
            "article": {
                "share_with": "kakaemma.com",
                "content": "music-in-town"
            }
        }
        self.no_content = {
            "article": {
                "share_with": "",
                "content": ""
            }
        }

        self.response = self.client.post(
            '/api/users/', self.user_data, format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.response.data['auth_token']
        )

        self.title = 'test article'
        self.description = 'an article to test model'
        self.body = 'This article will test our model'
        self.tagList = [ "articles", "authors", "TEST"]

        self.article = {'article': {'title': self.title,
                                    'description': self.description,
                                    'body': self.body}}
        self.article_with_tags = {'article': {'title': self.title,
                                    'description': self.description,
                                    'body': self.body,
                                    'tagList': self.tagList}}
        self.update_data = {'article': {'body': "This ought to work"}}
  
        self.response = self.client.post('/api/articles/', self.article,
                                    format="json")
        self.response1 = self.client.post('/api/articles/',
                                     self.article, format="json")
        self.response3 = self.client.post('/api/articles/', self.article_with_tags,
                                    format="json")
                                    
    def method_to_call_on_route(self, end_point, endpoint_data):
        response = self.client.post(end_point, endpoint_data, format="json" )
        return response

    def test_can_create_article(self):
        response = self.client.post('/api/articles/', self.article,
                                    format="json")
        self.response1 = self.client.post('/api/articles/',
                                     self.article, format="json")
        self.response3 = self.client.post('/api/articles/', self.article_with_tags,
                                    format="json")
    def test_can_create_article(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_can_create_article_with_tags(self):
        self.assertEqual(self.response3.status_code, status.HTTP_201_CREATED)

    def test_can_get_article(self):
        result = self.client.get('/api/articles/{}/'
                                 .format(self.response.data['article']['slug']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_can_update_article(self):
        result = self.client.put('/api/articles/{}/'
                                 .format(self.response.data['article']['slug']),
                                 self.update_data, format="json")
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_can_delete_article(self):
        result = self.client.delete('/api/articles/{}/'
                                    .format(self.response.data['article']['slug']))
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)        

    def test_can_not_edit_unless_author(self):
        response = self.client.put('/api/articles/{}/'.format("no-work"),
                                   self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_not_delete_unless_author(self):
        response = self.client.delete('/api/articles/{}/'.format("no-work"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_unique_slug(self):
        self.assertNotEqual(self.response, self.response1)

    def test_can_get_all_articles(self):
        self.client.post('/api/articles/', self.article, format="json")
        self.client.post('/api/articles/', self.article, format="json")
        response = self.client.get('/api/article/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_article_that_doesnot_exist(self):
        response = self.client.get('/api/articles/{}/'.format("no-work-here"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_get_all_tags(self):
        result = self.client.get('/api/tags/')
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_share_article(self):
        resp = self.method_to_call_on_route('/api/article/share/', self.share_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_share_article_with_invalid_email(self):
        response = self.method_to_call_on_route('/api/article/share/', self.invalid_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_article_with_no_content(self):
        response = self.method_to_call_on_route('/api/article/share/', self.no_content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_return_articles_for_user(self):
        result = self.client.get('/api/article/my-articles/')
        self.assertEqual(result.status_code, status.HTTP_200_OK)


class ReactionViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.username = "johndoe"
        self.email = "johndoe@gmail.com"
        self.password = "Password1"

        self.user_data = {
            "user": {
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
        }

        self.response = self.client.post(
            '/api/users/', self.user_data, format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(self.response.data['auth_token'])
        )

        self.title = 'test article'
        self.description = 'an article to test model'
        self.body = 'This article will test our model'
        self.slug = 'test-article'

        self.article = {
            'article': {
                'title': self.title,
                'description': self.description,
                'body': self.body
            }
        }
        self.client.post('/api/articles/', self.article, format="json")

        populate_impression_table()

        self.reactions = [
            {'reaction': 'Like'},
            {'reaction': 'Dislike'},
            {'reaction': 'Favourite'}
        ]
        self.response = []
        for reaction in self.reactions:
            reaction_response = self.post_reaction(reaction)
            self.response.append(reaction_response)

    def post_reaction(self, reaction):
        response = self.client.post(
            '/api/articles/{0}/reaction/'.format(
                self.slug
            ), reaction, format="json"
        )
        return response

    def test_can_react_to_an_article(self):
        response_count = 0
        for reaction in self.reactions:
            self.assertEqual(
                self.response[response_count].status_code, status.HTTP_200_OK
            )
            response_count += 1

    def test_can_remove_reaction(self):
        for reaction in self.reactions:
            response = self.client.delete(
                '/api/articles/{0}/reaction/'.format(self.slug),
                reaction, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_not_react_more_than_once(self):
        for reaction in self.reactions:
            response = self.post_reaction(reaction)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_not_remove_non_existing_reaction(self):
        for reaction in self.reactions:
            response = self.client.delete(
                '/api/articles/{0}/reaction/'.format(self.slug),
                reaction, format="json"
            )
            response = self.client.delete(
                '/api/articles/{0}/reaction/'.format(self.slug),
                reaction, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  


class ReactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="raddish", email="rad@gmail.com", password="radredrad1"
        )
        self.old_count = Reaction.objects.count()
        self.article = Article.objects.create(
            title="my article", description="test",body="testing article"
        )
        self.reaction = Impression
        self.like_impression = Impression.objects.create(
            name='Like', description='Person finds the article appeasing'
        )
        self.dislike_impression = Impression.objects.create(
            name='Dislike',
            description='Person does not find the article to their liking'
        )
        self.favourite_impression = Impression.objects.create(
            name='Favourite',
            description="Person has found that they resonate with an article's words"
        )
        self.reactions = [self.like_impression, self.dislike_impression, self.favourite_impression]

    def create_reaction(self, reaction):
        Reaction.objects.create(
            article=self.article, user=self.user, reaction=reaction
        )

    def test_model_can_react_to_article(self):
        for reaction in self.reactions:
            self.create_reaction(reaction=reaction)
            self.new_count = Reaction.objects.count()
            self.assertNotEqual(self.old_count, self.new_count)

    def test_model_delete_reaction(self):
        for reaction in self.reactions:
            self.create_reaction(reaction=reaction)
            reaction = Reaction.objects.get(
                article=self.article, user=self.user, reaction=reaction
            )
            reaction.delete()
            self.new_count = Reaction.objects.count()
            self.assertEqual(self.old_count, self.new_count)


class ArticlesModelTestCase(TestCase):
    """Class with tests to do with interacting with the article model"""

    def setUp(self):
        """Define the test variables"""
        self.user = User.objects.create_user(
            username="red", email="red@gmail.com", password="password"
        )
        self.profile = Profile.objects.get(user=self.user)
        self.old_count = Article.objects.count()
        self.article = Article.objects.create(
            title="Test article",
            description="description of test article",
            body="this is the body of test article",
            author=self.profile
        )

    def test_creation_of_article(self):
        """Test that an article can be created."""
        self.new_count = Article.objects.count()
        self.assertNotEqual(self.old_count, self.new_count)

    def test_get_an_article_by_anyone(self):
        """Test that an article can be returned."""
        article = self.article.get_article('test-article')
        self.assertEqual(article.description, "description of test article")

    def test_an_article_can_be_deleted(self):
        """Test that an article can be deleted."""
        self.article.delete_article(self.user.email, 'test-article')
        self.new_count = Article.objects.count()
        self.assertEqual(self.old_count, self.new_count)


    def test_get_article_by_authenticated_user(self):
        """Test that an authenticated user can get an article"""
        protected_article = self.article.get_user_article(
            self.user.email, 'test-article'
        )
        self.assertEqual(protected_article.description, "description of test article")


class TestPopulateTable(TestCase):
    def test_table_is_populated(self):
        out = StringIO()
        call_command('populate_impression', stdout=out)
        self.assertIn('Impression Table has been populated', out.getvalue())

    def test_table_has_already_been_populated(self):
        out = StringIO()
        populate_impression_table()
        call_command('populate_impression', stdout=out)
        self.assertIn('No need to populate Impression table.', out.getvalue())

def populate_impression_table():
    impressions = [
        {'Like': 'Person finds the article appeasing'},
        {'Dislike': 'Person does not find the article to their liking'},
        {'Favourite': "Person has found that they resonate with an article's words"}
    ]
    for impression in impressions:
        for key in impression:
            Impression.objects.create(
                name=key,
                description=impression[key]
            ).save()


class TestReadingTime(TestCase):
    body = "one two three\n four five six \n"

    def test_correct_time_returned(self):
        time = Article.article_reading_time(self.body * 200)
        self.assertEqual(time, '4 minutes')

    def test_correct_time_less_than_2_minutes(self):
        time = Article.article_reading_time(self.body * 75)
        self.assertEqual(time, 'About 1 minute')

    def test_correct_time_less_than_1_minute(self):
        time = Article.article_reading_time(self.body * 20)
        self.assertEqual(time, 'Less than a minute')


class ViewTestComments(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "johndoe"
        self.email = "johndoe@gmail.com"
        self.password = "Password1"
        self.user_data = {
            "user": {
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
        }
        self.response = self.client.post(
            '/api/users/', self.user_data, format="json"
        )
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(self.response.data['auth_token'])
        )
        self.title = 'test article'
        self.description = 'an article to test model'
        self.body = 'This article will test our model'
        self.article = {
            'article': {
                'title': self.title,
                'description': self.description,
                'body': self.body
            }
        }

        self.comment_body = "this is my comment"

        self.comment = {
            "comment": {
                "body": self.comment_body
            }
        }

        self.thread = {
            "comment": {
                "body": "lets start a thread one"
            }
        }

        self.create_article = self.client.post(
            '/api/articles/', self.article, format="json"
        )

        self.create_comment = self.client.post(
            '/api/articles/{}/comments/'.format(
                self.create_article.data['article']['slug']
            ),
            self.comment, format="json"
        )

        self.create_thread = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            ),
            self.thread, format="json"
        )

    def test_comment_creation(self):
        self.assertEqual(
            self.create_comment.status_code,status.HTTP_201_CREATED
        )

    def test_comment_retrieval(self):
        result = self.client.get(
            '/api/articles/{}/comments/'.format(
                self.create_article.data['article']['slug']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_comment_update(self):
        result = self.client.put(
            '/api/articles/{}/comments/{}/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            ),
            self.comment, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_comment_delete(self):
        result = self.client.delete(
            '/api/articles/{}/comments/{}/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("comment has been deleted successfully",
                      str(result.data['message']))
    
    def test_comment_delete_with_non_existent_article(self):
        result = self.client.delete(
            '/api/articles/no_article/comments/{}/'.format(
                self.create_comment.data['id']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The Article does not exist",
                      str(result.data['detail']))

    def test_thread_creation(self):
        result = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_thread_retrieval(self):
        result = self.client.get(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_comment_for_non_existent_article(self):
        result = self.client.post(
            '/api/articles/non-existent/comments/',
            self.comment, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The Article does not exist", str(result.data['detail']))

    def test_update_non_existent_comment(self):
        result = self.client.put(
            '/api/articles/{}/comments/{}/'.format(
                self.create_article.data['article']['slug'], int(100)
            ),
            self.comment, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The comment does not exist", str(result.data['detail']))

    def test_thread_creation_with_non_existent_article(self):
        result = self.client.post(
            '/api/articles/no-article/comments/{}/thread/'.format(
                self.create_comment.data['id']
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The Article does not exist", str(result.data['detail']))

    def test_thread_creation_with_non_existent_parent_comment(self):
        result = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'], int(30)
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The parent comment does not exist",
                      str(result.data['detail']))

    def test_thread_creation_with_another_thread_as_parent(self):
        result = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_thread.data['id']
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Parent comment is already a sub comment",
            str(result.data['message'])
        )
