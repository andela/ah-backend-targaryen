import json

from rest_framework.renderers import JSONRenderer
from authors.apps.core.renderers import AuthorsJSONRenderer


class UserJSONRenderer(AuthorsJSONRenderer):
    object_label = 'user'

    def render(self, data, media_type=None, renderer_context=None):

        return super(UserJSONRenderer, self).render(data)
