from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authors.apps.authentication.backends import JWTAuthentication
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .models import Profile


class ProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def retrieve(self, request, username, *args, **kwargs):
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise TypeError('Profile does not exist')

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_data = request.data.get('profile', {})

        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'bio': user_data.get('bio', request.user.profile.bio),
            'avatar': user_data.get('avatar', request.user.profile.avatar)
        }

        serializer = self.serializer_class(
            request.user.profile, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user.profile, serializer_data)

        serializer.update(request.user, serializer_data)

        return Response(serializer.data, status=status.HTTP_200_OK)
