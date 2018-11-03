from .renderers import UserJSONRenderer
from rest_framework.permissions import(
 AllowAny,
 IsAuthenticated
)


class AttributeMixins:
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)


class AuthenticatedUserMixins:
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
