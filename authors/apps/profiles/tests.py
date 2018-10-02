# tests for authentication application
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from authors.apps.authentication.models import User
from authors.apps.profiles.models import User


class ViewTestCase(TestCase):
    """Class with tests to do with profile views"""

    def setUp(self):
        """Define the test client and test variables"""
        self.client = APIClient()

        self.username = "johndoe"
        self.email = "johndoe@gmail.com"
        self.password = "Password1"
        self.bio = "johndoe bio"
        self.avatar = "https://google.com/pagenotfound/"

        self.user_data = {"user": {"username": self.username,
                                   "email": self.email,
                                   "password": self.password}}
        self.profile_data = {"profile": {"username": self.username,
                                         "bio": self.bio,
                                         "avatar": self.avatar}}

        self.response = self.client.post(
            '/api/users/', self.user_data, format="json")

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.response.data['auth_token']
        )

    def test_profile_retreival(self):
        """Tests that a profile is created and retreived"""
        response = self.client.get(
            '/api/profiles/{}'.format(self.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_update(self):
        """Tests that a profile can be updated by a user"""
        response = self.client.put(
            '/api/profiles/update/', data=self.profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.profile_data['profile']['username'], response.data['username']
            )
        self.assertIn(
            self.profile_data['profile']['bio'], response.data['bio']
            )
        self.assertIn(
            self.profile_data['profile']['avatar'], response.data['avatar']
        )
