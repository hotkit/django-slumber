"""Implements the conversion of the response data to valid xml data.
"""
from __future__ import absolute_import

import dicttoxml
from django.http import HttpResponse
from xml.dom.minidom import parseString


def as_xml(request, response, content_type):
    """Return http response object in text/xml format.
    """
    xml_snippet = dicttoxml.dicttoxml(response, root=True)
    dom = parseString(xml_snippet).toprettyxml()
    return HttpResponse(dom, 'text/xml', status=response['_meta']['status'])
