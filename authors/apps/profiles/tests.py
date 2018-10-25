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
        self.unauthorized_client = APIClient()

        self.username = "johndoe"
        self.email = "johndoe@gmail.com"
        self.password = "Password1"
        self.bio = "johndoe bio"
        self.avatar = "https://google.com/pagenotfound/"

        self.other_username = "janedoe"
        self.other_email = "janedoe@gmail.com"
        self.other_password = "Password1"
        self.other_bio = "janedoe bio"
        self.other_avatar = "https://google.com/pagenotfound/"

        self.user_data = {
            "user": {
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
        }
        self.profile_data = {
            "profile": {
                "username": self.username,
                "bio": self.bio,
                "avatar": self.avatar
            }
        }
        
        self.other_user_data = {
            "user": {
                "username": self.other_username,
                "email": self.other_email,
                "password": self.other_password
            }
        }
        self.other_profile_data = {
            "profile": {
                "username": self.other_username,
                "bio": self.other_bio,
                "avatar": self.other_avatar
            }
        }

        self.other_response = self.client.post(
            '/api/users/', self.other_user_data, format="json"
        )

        self.response = self.client.post(
            '/api/users/', self.user_data, format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(self.response.data['auth_token'])
        )

        self.follow_response = self.client.post(
            '/api/profiles/{}/follow/'.format(self.other_username)
        )

    def test_profile_retreival(self):
        """Tests that a profile is created and retreived"""
        response = self.client.get(
            '/api/profiles/{}/'.format(self.username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_retreival_without_authentication(self):
        """Tests that a profile cant be retrieved without authentication"""
        response = self.unauthorized_client.get(
            '/api/profiles/{}/'.format(self.username)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_update(self):
        """Tests that a profile can be updated by a user"""
        response = self.client.put(
            '/api/profiles/update/', data=self.profile_data, format='json'
        )
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

    def test_profile_update_without_authentication(self):
        """Tests that a profile cant be updated without authentication"""
        response = self.unauthorized_client.put(
            '/api/profiles/update/', data=self.profile_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieval_of_all_user_profiles(self):
        """Tests that all user profiles can be retrieved"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_retrieval_of_all_user_profiles(self):
        """Tests that all profiles cant be retrieves without authentication"""
        response = self.unauthorized_client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_follow_user(self):
        self.assertEqual(self.follow_response.status_code, status.HTTP_200_OK)
    
    def test_follow_user_already_being_followed(self):
        response = self.client.post(
            '/api/profiles/{}/follow/'.format(self.other_username)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unfollow_user(self):
        response = self.client.delete(
            '/api/profiles/{}/unfollow/'.format(self.other_username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_follow_yourself(self):
        response = self.client.delete(
            '/api/profiles/{}/unfollow/'.format(self.username)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_non_existent_user(self):
        response = self.client.post(
            '/api/profiles/{}/follow/'.format("no_user")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_non_existent_user(self):
        response = self.client.delete(
            '/api/profiles/{}/unfollow/'.format("no_user")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unfollow_user_not_being_followed(self):
        self.client.delete(
            '/api/profiles/{}/unfollow/'.format(self.other_username)
        )
        response = self.client.delete(
            '/api/profiles/{}/unfollow/'.format(self.other_username)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unfollow_user_with_no_authentication(self):
        response = self.unauthorized_client.delete(
            '/api/profiles/{}/unfollow/'.format(self.other_username)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_follow_user_with_no_authentication(self):
        response = self.unauthorized_client.post(
            '/api/profiles/{}/follow/'.format(self.other_username)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
