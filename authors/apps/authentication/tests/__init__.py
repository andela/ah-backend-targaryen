import datetime
import jwt
from decouple import config
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User, UserManager
from authors.apps.authentication.validators import ValidateUserDetails


class BaseTestCase(TestCase):

    def setUp(self):
        """Test registration api views"""
        self.client = APIClient()

        self.user_data = {"user": {"username": "samuel",
                                   "email": "samuel@gmail.com",
                                   "password": "password1"}}
        self.user_data_token = {"user": {"username": "user1",
                                         "email": "user1@gmail.com",
                                         "password": "password1"}}
        self.user_existing_email = {'user': {
                                    'username': 'samuel',
                                    'email': 'samuel@gmail.com',
                                    'password': 'password1'}}
        self.user_invalid_email = {'user': {
            'username': 'samuel',
            'email': 'samuelgmail.com',
            'password': 'password1'}}
        self.user_missing_password = {'user': {
            'username': 'baron',
            'email': 'baron@gmail.com',
            'password': None}}
        self.user_missing_email = {'user': {
            'username': 'samuel',
            'email': None,
            'password': 'password1'}}
        self.user_missing_name = {'user': {
            'username': None,
            'email': 'bridget@gmail.com',
            'password': 'password_bridget1'}}
        self.user_non_alphanumeric_password = {'user': {
            'username': 'samuel',
            'email': 'samuel@gmail.com',
            'password': 'passworddd'}}
        self.user_username_less_than_four = {'user': {
            'username': 'sam',
            'email': 'samuel@gmail.com',
            'password': 'password1'}}
        self.user_password_less_than_eight = {'user': {
            'username': 'sam',
            'email': 'samuel@gmail.com',
            'password': 'pwd1'}}
        self.user_forgotten_password = {'user': {
                                    'username': 'samuel',
                                    'email': 'samuel@gmail.com'}}
        self.user_update_password = {"user": {"username": "samuel",
                                   "email": "samuel@gmail.com",
                                   "password": "password123"}}
        self.no_such_user_update_password = {"user": {"username": "buttons",
                                   "email": "buttons@gmail.com",
                                   "password": "password123"}}
        self.token = jwt.encode(
                {
                    'name': self.user_forgotten_password['user']['username'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(
                        minutes=60)},
                config('SECRET_KEY')).decode('UTF-8')
        self.non_existing_user_token = jwt.encode(
                {
                    'name': self.no_such_user_update_password['user']['username'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(
                        minutes=60)},
                config('SECRET_KEY')).decode('UTF-8')
        self.login_details = {
            "user": {"email": "samuel@gmail.com", "password": "password1"}}
        self.login_details_token = {
            "user": {"email": "samuel@gmail.com", "password": "password1"}}
        self.login_invalid_email = {
            "user": {"email": "samuelgmail.com", "password": "password1"}}
        self.login_wrong_email = {
            "user": {"email": "wrong@wrong.com", "password": "password1"}}
        self.login_wrong_password = {
            "user": {"email": "samuel@gmail.com", "password": "wrongggg"}}
        self.response = self.client.post(
            '/api/users/', self.user_data, format="json")

        self.user = {"user": {"username": "sam",
                              "email": "samuelgmail.com",
                              "password1": "passwor",
                              "password2": "passworddd"}}

        self.old_count = User.objects.count()
        self.second_user = User.objects.create_user(
            username="david", email="david@gmail.com", password="password")

        self.validator = ValidateUserDetails()

        # Profile data

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

