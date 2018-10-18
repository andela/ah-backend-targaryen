from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError


class GoogleAuthentication:
    """
    Class handling google authentication
    """
    @staticmethod
    def validate_google_token(
            auth_token, refresh_token=None, access_token=None
        ):
        """
        This method validates the google auth token
        :param auth_token: Token from the client
        :param refresh_token: helps refresh the token if it's expired
        :param access_token: access token from the client
        :return:
        """
        try:
            token_uri = "https://www.googleapis.com/oauth2/v4/token"
            credentials = Credentials(access_token,
                                      refresh_token=refresh_token,
                                      id_token=auth_token,
                                      token_uri=token_uri,
                                      client_id=config('GOOGLE_CLIENT_ID'),
                                      client_secret=config('GOOGLE_SECRET')
                                      )
            try:
                credentials.refresh(requests.Request())
            except RefreshError:
                pass        
            auth_token = credentials.id_token
            user_info = id_token.verify_oauth2_token(
                auth_token, requests.Request(), config('GOOGLE_CLIENT_ID'))
            return user_info
        except ValueError:
            msg = "Invalid or expired token"
            return msg
