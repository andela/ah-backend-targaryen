from django.urls import path

from .views import CreateArticle, ArticleRetrieveUpdate, ArticleList

urlpatterns = [
    path('articles/', CreateArticle.as_view()),
    path('articles/<str:slug>/', ArticleRetrieveUpdate.as_view()),
    path('article/', ArticleList.as_view())
]
