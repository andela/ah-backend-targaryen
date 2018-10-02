import facebook


class FacebookAuthentication:
    """
    Class Handling Facebook authentication
    """

    @staticmethod
    def validate_token(auth_token):
        """
        This method validates the facebook authorisation token
        :param auth_token:
        :return: user_data
        """
        try:
            # create an instance of the facebook graph
            facebook_graph = facebook.GraphAPI(
                access_token=auth_token, version="3.0"
            )
            # Get user data
            user_data = facebook_graph.request('/me?fields=id,name,email')
            return user_data
        except facebook.GraphAPIError:
            msg = "Invalid or expired token"
            return msg
