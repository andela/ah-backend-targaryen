import jwt
from decouple import config
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header)

from .models import User


class JWTAuthentication(BaseAuthentication):
    """Authentication class called in views"""
    authentication_header_name = 'Token'

    def authenticate(self, request):
        """
        Splits the token header and
        passes the result to the _authenticate_data method
        """
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header:
            return None

        name = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        return self._authenticate_data(request, token)

    def _authenticate_data(self, request, token):
        """
        Authenticates data received from the authenticate method and
        returns a token to the user
        """
        try:
            result = jwt.decode(token, config('SECRET_KEY'))
        except:
            message = 'Failed to decode token'
            raise exceptions.AuthenticationFailed(message)

        try:
            user = User.objects.get(username=result['name'])
        except User.DoesNotExist:
            message = 'No user was found'
            raise exceptions.AuthenticationFailed(message)

        if not user.is_active:
            message = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(message)
        return (user, token)
