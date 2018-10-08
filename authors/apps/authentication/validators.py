import re

from pyisemail import is_email
from rest_framework import serializers


class ValidateUserDetails:
    """Class adds validator methods for user details"""
    
    def is_password_valid(self, password):
        if len(password) < 8:
            raise serializers.ValidationError(
                {'password': 'The password should be atleast 8 characters'}
            )
        if (re.match('(?=.*[0-9])(?=.*[a-zA-Z])', password)) is None:
            raise serializers.ValidationError(
                {'password': 'The password should have atleast one number and a letter'}
            )

    def is_username_valid(self, username):
        if len(username) < 4:
            raise serializers.ValidationError(
                {'username': 'The username should be atleast 4 characters'}
            )

    def is_email_valid(self, email):
        if not is_email(email):
            raise serializers.ValidationError(
                {'email': 'Enter a valid email address.'}
            )
