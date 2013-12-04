""" Handler for handle http accept header
"""
from simplejson import dumps

from django.http import HttpResponse
from django.conf import settings

import slumber


def default_handler(_request, response, _content_type):
    """Implement the default accept handling which will return JSON data.
    """
    if settings.DEBUG:
        dump_content = dumps(
            response, indent=4,
            cls=slumber.server.http._proxyEncoder)
    else:
        dump_content = dumps(
            response, cls=slumber.server.http._proxyEncoder)

    return HttpResponse(
        dump_content, 'text/plain',
        status=response['_meta']['status'])
