from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Article


class ViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.username = "johndoe"
        self.email = "johndoe@gmail.com"
        self.password = "Password1"

        self.user_data = {"user": {"username": self.username,
                            "email": self.email,
                            "password": self.password}}

        self.response = self.client.post('/api/users/', self.user_data, format="json")

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.response.data['auth_token']
        )

        self.title = 'test article'
        self.description = 'an article to test model'
        self.body = 'This article will test our model'

        self.article = {'article': {'title': self.title,
                                    'description': self.description,
                                    'body': self.body}}
        self.update_data = {'article': {'body': "This ought to work"}}
  
    
    def test_can_create_article(self):
        response = self.client.post('/api/articles/', self.article,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_get_article(self):
        response = self.client.post('/api/articles/', self.article,
                                    format="json")
        result = self.client.get('/api/articles/{}/'
                                 .format(response.data['article']['slug']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_can_update_article(self):
        response = self.client.post('/api/articles/', self.article,
                                    format="json")
        result = self.client.put('/api/articles/{}/'
                                 .format(response.data['article']['slug']),
                                 self.update_data, format="json")
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_can_delete_article(self):
        response = self.client.post('/api/articles/', self.article,
                                    format="json")
        result = self.client.delete('/api/articles/{}/'
                                    .format(response.data['article']['slug']))
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)        
    
    def test_can_not_edit_unless_author(self):
        response = self.client.put('/api/articles/{}/'.format("no-work"),
                                   self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_can_not_delete_unless_author(self):
        response = self.client.delete('/api/articles/{}/'.format("no-work"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_unique_slug(self):
        response = self.client.post('/api/articles/',
                                    self.article, format="json")
        response1 = self.client.post('/api/articles/',
                                     self.article, format="json")
        self.assertNotEqual(response, response1)

    def test_can_get_all_articles(self):
        self.client.post('/api/articles/', self.article, format="json")
        self.client.post('/api/articles/', self.article, format="json")
        response = self.client.get('/api/article/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_article_that_doesnot_exist(self):
        response = self.client.get('/api/articles/{}/'.format("no-work-here"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
