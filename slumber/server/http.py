"""
    Implements the conversion of the response data to valid HTTP
    data.
"""
from simplejson import dumps

from django.http import HttpResponse


def view_handler(view):
    """Wrap a view function so it can return either JSON, HTML or some
    other response.
    """
    def wrapper(request, *args, **kwargs):
        """The decorated implementation.
        """
        response = {'_meta': dict(status=200, message='OK')}
        http_response = view(request, response, *args, **kwargs)
        if not http_response:
            http_response = HttpResponse(dumps(response, indent=4), 'text/plain')
            http_response.status_code = response['_meta']['status']
        return http_response
    return wrapper
