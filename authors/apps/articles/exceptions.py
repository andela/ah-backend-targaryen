"""
Class to handle exceptions
"""

from rest_framework.exceptions import APIException


class NotFoundException(APIException):
    """
    Provides 404 not found error
    """
    default_code = "not_found"
    default_detail = "The requested resource was not found."
    status_code = 404
