from .renderers import (
    ArticleJSONRenderer,
    ReactionJSONRenderer,
    CommentJSONRenderer,
    ThreadJSONRenderer
)
from .serializers import (
    ArticleSerializer,
    ReactionSerializer,
    TagSerializer,
    CommentSerializer,
    ShareArticleSerializer
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny
)
class ArticleMixin:
    serializer_class = ArticleSerializer
    renderer_class = (ArticleJSONRenderer,)
    permission_classes = (IsAuthenticated,)

class CommentsMixin:
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

