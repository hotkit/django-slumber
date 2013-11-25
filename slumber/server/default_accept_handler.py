""" Handler for handle http accept header
"""

import slumber
from django.http import HttpResponse
from simplejson import dumps
from django.conf import settings


def default_handler(request, response, content_type):
    if settings.DEBUG:
        dump_content = dumps(
            response,
            indent=4,
            cls=slumber.server.http._proxyEncoder
        )
    else:
        dump_content = dumps(
            response,
            cls=slumber.server.http._proxyEncoder
        )

    return HttpResponse(
        dump_content,
        'text/plain',
        status=response['_meta']['status']
    )
