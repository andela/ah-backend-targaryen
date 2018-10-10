import json
from rest_framework.renderers import JSONRenderer


class ArticleJSONRenderer(JSONRenderer):
    """Class for JSON renderer for Artiles app"""
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """Method to convert data to a specific format
        :params data
        :return JSON object with key article"""

        return json.dumps({'article': data})
