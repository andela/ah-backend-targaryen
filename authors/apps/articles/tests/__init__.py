from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class BaseTestCaseArticles(TestCase):
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
        # comments
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
