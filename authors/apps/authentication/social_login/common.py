from django.contrib.auth import authenticate

from rest_framework import serializers
from authors.apps.authentication.models import User
from decouple import config


def create_user_and_return_token(user_id, name, email):
    """
    Method to register a user and return a token
    :param user_id:
    :param name:
    :param email:
    :return: auth_token
    """
    # check if the user has registered with social auth
    social_user = User.objects.filter(social_auth_id=user_id)

    if not social_user.exists():
        user = {
            'email': email,
            'username': name,
            'password': config('DEFAULT_PASS')
        }
        try:
            User.objects.create_user(**user)
        except:
            raise serializers.ValidationError(
                "Email " + email + " has already been used"
            )
        User.objects.filter(email=email).update(
            social_auth_id=user_id
        )
        auth_user = authenticate(
            email=email, password=config('DEFAULT_PASS')
        )
        return auth_user.auth_token
    else:
        auth_user = authenticate(
            email=email, password='defaultpass'
        )
        return auth_user.auth_token
