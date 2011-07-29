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
        response = {}
        http_response = view(request, response, *args, **kwargs)
        if http_response:
            return http_response
        else:
            return HttpResponse(dumps(response, indent=4), 'text/plain')
    return wrapper
