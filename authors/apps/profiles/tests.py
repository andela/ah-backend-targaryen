# tests for authentication application
from authors.apps.authentication.tests import BaseTestCase
from rest_framework import status


class ViewTestCase(BaseTestCase):
    """Class with tests to do with profile views"""

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
