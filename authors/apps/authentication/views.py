import re
from datetime import datetime, timedelta
from threading import Thread

import jwt
import sendgrid
from decouple import config
from rest_framework import serializers, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sendgrid.helpers.mail import *

from .backends import JWTAuthentication
from .renderers import UserJSONRenderer
from .serializers import (LoginSerializer, RegistrationSerializer,
                          UserSerializer)


def generate_ver_token(data, time):
    """
    Generates a verification token on registering a user and has an expiry
    date set to 60 days.
    """
    data_to_encode = {'exp': datetime.utcnow() + timedelta(
                        days=time),
                        }
    #check what type of data is encoded
    if isinstance(data, dict):
        data_to_encode['name'] = data['username']
    else:
        data_to_encode['email'] = data
    ver_token = jwt.encode(
        data_to_encode,
        config('SECRET_KEY'), algorithm='HS256').decode('utf-8')
    return ver_token

def send_mail(user_mail, mail_subject, content):
    sg = sendgrid.SendGridAPIClient(apikey=config('SENDGRID_API_KEY'))
    from_email = Email("targaryen@authorshaven.com")
    to_email = Email(user_mail)
    subject = mail_subject
    mail = Mail(from_email, subject, to_email, content)
    res = sg.client.mail.send.post(request_body=mail.get())
    return res

def send_verification_link(user_email, token):
    """
    Sends a an email with a verification link upon successful
    registration os a user.
    """
    subject = "Authors Haven verification link"
    content = Content(
        "text/plain",
        "Click on the link below to verify your account. \n http://{}".format(token))
    #Run the sending of the mail in the background
    response = send_mail(user_email, subject, content)
    return response


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
        ver_token = generate_ver_token(user_email, 60)
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


class ResetPasswordAPIView(APIView):
    '''This view class is accessed using a post method which is
    used to send a token to a users email'''
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        '''Create a password-reset-token and send it in an email'''

        serializer_data = request.data.get('user', {})

        # Create the token that expires after 60 minutes
        token = generate_ver_token(serializer_data, 1/24)

        # render email text
        to_email = serializer_data['email']
        subject = "Password reset link"
        content = Content(
            "text/html",
            '<p>Use this token to reset password</p>\n<p>' +
            token + '</p>')
        send_mail(to_email, subject, content)
        return Response(
            {'message': 'Check your email for reset password'}, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        '''Use token received in email to resett password'''
        serializer_data = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        if len(serializer_data['password']) < 8:
            raise serializers.ValidationError(
                'The password should be atleast 8 characters'
            )
        elif (re.match('(?=.*[0-9])(?=.*[a-zA-Z])', serializer_data['password'])) is None:
            raise serializers.ValidationError(
                'The password should have atleast one number and a letter'
            )
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Successfully updated password'}, status=status.HTTP_201_CREATED)
