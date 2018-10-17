from django.urls import path

from .views import CreateArticle, ArticleRetrieveUpdate, ArticleList, TagList

urlpatterns = [
    path('articles/', CreateArticle.as_view()),
    path('articles/<str:slug>/', ArticleRetrieveUpdate.as_view()),
    path('article/', ArticleList.as_view()),
    path('tags/', TagList.as_view())
]
