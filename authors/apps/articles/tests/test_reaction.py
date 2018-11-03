from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article, Impression, Reaction


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