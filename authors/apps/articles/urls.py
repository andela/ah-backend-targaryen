from django.urls import path

from .views import (
    CreateArticle,
    ArticleRetrieveUpdate,
    ArticleList,
    ReactionView,
    TagList,
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    ThreadListCreateAPIView,
    ShareArticle
)

urlpatterns = [
    path('articles/', CreateArticle.as_view()),
    path('articles/<str:slug>/', ArticleRetrieveUpdate.as_view()),
    path('article/', ArticleList.as_view()),
    path('tags/', TagList.as_view()),
    path('articles/<str:slug>/reaction/', ReactionView.as_view()),
    path('articles/<str:slug>/comments/', CommentListCreateAPIView.as_view()),
    path('articles/<str:slug>/comments/<str:id>/',
         CommentRetrieveUpdateDestroyAPIView.as_view()
         ),
    path('articles/<str:slug>/comments/<int:id>/thread/',
         ThreadListCreateAPIView.as_view()
         ),
    path('article/share/', ShareArticle.as_view()),
]
