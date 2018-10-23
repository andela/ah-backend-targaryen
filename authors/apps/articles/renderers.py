import json
from rest_framework.renderers import JSONRenderer

from authors.apps.core.renderers import AuthorsJSONRenderer


class ArticleJSONRenderer(JSONRenderer):
    """Class for JSON renderer for Artiles app"""
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """Method to convert data to a specific format
        :params data
        :return JSON object with key article"""

        return json.dumps({'article': data})


class ReactionJSONRenderer(JSONRenderer):
    """Class to render reactions"""
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """Method to convert data to a specific format
        :params data
        :return JSON object with key reaction"""

        return json.dumps({'reaction': data})


class CommentJSONRenderer(AuthorsJSONRenderer):
    """Renderer for the comments"""
    object_label = 'comments'


class ThreadJSONRenderer(AuthorsJSONRenderer):
    """Renderer for the comments"""
    object_label = 'thread'
