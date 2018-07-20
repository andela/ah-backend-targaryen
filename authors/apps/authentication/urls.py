from django.conf.urls import url
from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

# urlpatterns = [
#     url(r'^user/?$', UserRetrieveUpdateAPIView.as_view()),
#     url(r'^users/?$', RegistrationAPIView.as_view()),
#     url(r'^users/login/?$', LoginAPIView.as_view()),
# ]


# Use the new path module in django 2.0
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
]