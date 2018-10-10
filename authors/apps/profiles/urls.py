from django.urls import path

from .views import (
    ProfileRetrieveUpdateAPIView,
    ProfileList
)

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveUpdateAPIView.as_view()),
    path('profiles/update/', ProfileRetrieveUpdateAPIView.as_view()),
    path('profile/', ProfileList.as_view()),
]
