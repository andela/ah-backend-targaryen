from django.shortcuts import render
from rest_framework import (
    status,
    serializers
)
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.authentication.backends import JWTAuthentication
from .renderers import ProfileJSONRenderer
from .serializers import (
    ProfileSerializer,
    ProfileListSerializer
)
from .models import Profile
from .exceptions import NotFoundException


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

        serializer = self.serializer_class(profile, context={'request': profile})

        return Response(serializer.data, status=status.HTTP_200_OK)

        current_user = self.request.user

    def update(self, request, *args, **kwargs):
        user_data = request.data.get('profile', {})

        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'bio': user_data.get('bio', request.user.profile.bio),
            'avatar': user_data.get('avatar', request.user.profile.avatar),
            'reading_stats': user_data.get('reading_stats', 
                            request.user.profile.reading_stats)
        }

        serializer = self.serializer_class(
            request.user.profile,
            data=serializer_data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user.profile, serializer_data)

        serializer.update(request.user, serializer_data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileList(RetrieveAPIView):
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def retrieve(self, request, *args, **kwargs):
        queryset = Profile.objects.all()
        serializer = self.serializer_class(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)


class FollowAPIView(APIView):
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, username=None):
        current_user = self.request.user

        try:
            follow = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFoundException("The user requested for does not exist")
        
        if follow.pk is current_user.pk:
            raise serializers.ValidationError("You can not follow yourself")
        
        current_user_profile = Profile.objects.get(user_id=current_user)

        if current_user_profile.is_following(follow):
            return Response(
                {"message": "You are already following this user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_user_profile.follow(follow)
        current_user_profile.save()

        serializer = self.serializer_class(
            current_user_profile, context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, username=None):
        current_user = self.request.user

        try:
            unfollow = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFoundException("The user requested for does not exist")
        
        current_user_profile = Profile.objects.get(user_id=current_user)

        if not current_user_profile.is_following(unfollow):
            return Response(
                {"message": "You cannot unfollow a user you do not follow"},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_user_profile.unfollow(unfollow)
        current_user_profile.save()

        serializer = self.serializer_class(
            current_user_profile, context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
