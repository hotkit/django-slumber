""" Handler for handle http accept header
"""

import slumber
from django.http import HttpResponse
from simplejson import dumps


def default_handler(request, response, content_type):
    return HttpResponse(
        dumps(
            response, indent=4,
            cls=slumber.server.http._proxyEncoder),
        'text/plain',
        status=response['_meta']['status']
    )
