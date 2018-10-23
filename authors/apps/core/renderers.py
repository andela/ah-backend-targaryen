import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import (
    ReturnDict,
    ReturnList
)

class AuthorsJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'
    
    def render(self, data, media_type=None, renderer_context=None):
        """Method to convert data to a specific format"""
        if type(data) != ReturnList:
            errors = data.get('errors', None)
            if errors is not None:
                return super(AuthorsJSONRenderer, self).render(data)

        if type(data) == ReturnDict:
            return json.dumps({self.object_label: data})

        else:
            return json.dumps({self.object_label: data})
