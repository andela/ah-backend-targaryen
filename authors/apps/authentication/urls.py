from django.urls import path

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    ResetPasswordAPIView,
    FacebookLoginAPIView,
    GoogleLoginAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('users/password_reset/', ResetPasswordAPIView.as_view()),
    path('users/password_update/', UserRetrieveUpdateAPIView.as_view()),
    path('auth/facebook/', FacebookLoginAPIView.as_view()),
    path('auth/google/', GoogleLoginAPIView.as_view())
]
