"""Implements the conversion of the response data to valid xml data.
"""
from __future__ import absolute_import

import dicttoxml
from django.conf import settings
from django.http import HttpResponse
from xml.dom.minidom import parseString


def as_xml(_request, response, content_type):
    """Return http response object in XML format.
    """
    xml = dicttoxml.dicttoxml(response, root=True)
    if settings.DEBUG:
        xml = parseString(xml).toprettyxml()
    return HttpResponse(xml, content_type,
        status=response['_meta']['status'])

