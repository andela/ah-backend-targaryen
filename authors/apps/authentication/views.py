import os
import ssl
from datetime import datetime, timedelta

import jwt
import sendgrid
from decouple import config
from rest_framework import serializers, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sendgrid.helpers.mail import *

from authors.apps.authentication.backends import JWTAuthentication
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
    )


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_email = serializer.data['email']
        ver_token = generate_ver_token(user_email)
        send_verification_link(user_email, ver_token)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('profile', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


def generate_ver_token(email):
    """
    Generates a verification token on registering a user and has an expiry
    date set to 60 days.
    """
    dt = datetime.now() + timedelta(days=60)
    ver_token = jwt.encode({
        'email': email,
        'exp': int(dt.strftime('%s'))},
        config('SECRET_KEY'), algorithm='HS256').decode('utf-8')
    return ver_token


def send_verification_link(user_email, token):
    """
    Sends a an email with a verification link upon successful
    registration os a user.
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    sg = sendgrid.SendGridAPIClient(apikey=config('SENDGRID_API_KEY'))
    from_email = Email("targaryen@authorshaven.com")
    to_email = Email(user_email)
    subject = "Authors Haven verification link"
    content = Content(
        "text/plain",
        "Click on the link below to verify your account. \n http://{}".format(token))
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
