import json
from decouple import config
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class SocialAuthTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_with_invalid_token ={
            "user":{
                "access_token": "invalid_fb_or_google_token"
            }
        }
        self.fb_user_with_valid_token ={
            "user":{
                "access_token": config('FACEBOOK_DEBUG_TOKEN')
            }
        }
        self.google_valid_token ={
            "user":{
                "access_token": config('GOOGLE_DEBUG_TOKEN'),
                "refresh_token": config('GOOGLE_REFRESH_TOKEN')
            }
        }

    def test_facebook_signup_with_invalid_token(self):
        """ Test for facebook user with invalid token"""
        response = self.client.post("/api/auth/facebook/",
                                    data=self.user_with_invalid_token,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["access_token"][0],
            "Invalid or expired token"
        )

    def test_facebook_signup_with_valid_token(self):
        """ Test for facebook user signup with valid token"""
        response = self.client.post("/api/auth/facebook/",
                                    data=self.fb_user_with_valid_token,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, 200)

    def test_facebook_login(self):
        """ Test for facebook login"""
        self.client.post("/api/auth/facebook/",
                         data=self.fb_user_with_valid_token,
                         format="json"
                         )
        response = self.client.post("/api/auth/facebook/",
                                    data=self.fb_user_with_valid_token,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, 200)

    def test_google_signup_with_invalid_token(self):
        """ Test for google user with invalid token"""
        response = self.client.post("/api/auth/google/",
                                    data=self.user_with_invalid_token,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["errors"]["access_token"][0],
            "Invalid or expired token"
        )
    
    def test_google_signup_with_valid_token(self):
        """ Test for google user with invalid token"""
        response = self.client.post("/api/auth/google/",
                                    data=self.google_valid_token,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, 200)

    def test_user_signup_with_same_email(self):
        """ Test for google user with using
        the same email
        """
        self.client.post("/api/auth/facebook/",
                         data=self.fb_user_with_valid_token,
                         format="json"
                         )
        response = self.client.post("/api/auth/google/",
                                    data=self.google_valid_token,
                                    format="json"
                                    )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Email",
            response.data["errors"]["access_token"][0]
        )
