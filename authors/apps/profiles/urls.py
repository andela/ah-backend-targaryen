from django.urls import path

from .views import (
    ProfileRetrieveUpdateAPIView,
    ProfileList,
    FollowAPIView
)

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveUpdateAPIView.as_view()),
    path('profiles/update/', ProfileRetrieveUpdateAPIView.as_view()),
    path('profile/', ProfileList.as_view()),
    path('profiles/<username>/follow/', FollowAPIView.as_view()),
    path('profiles/<username>/unfollow/', FollowAPIView.as_view()),
]
