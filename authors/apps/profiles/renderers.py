from authors.apps.core.renderers import AuthorsJSONRenderer

class ProfileJSONRenderer(AuthorsJSONRenderer):
    """Sub class of the renderers.py in core application"""
    object_label = 'profile'
