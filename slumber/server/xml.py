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
    if hasattr(response, 'root'):
        xml = dicttoxml.dicttoxml(response[response.root], root=False)
    else:
        xml = dicttoxml.dicttoxml(response, root=False)
    xml = ('<?xml version="1.0" encoding="UTF-8" ?>\n'
                    '<{root}>{document}</{root}>'.format(
                root=getattr(response, 'root', 'root'),
                document=xml))
    if settings.DEBUG:
        xml = parseString(xml).toprettyxml()

    if content_type is not None and 'charset' not in content_type:
            content_type += '; charset=utf-8'

    return HttpResponse(xml, content_type,
        status=response['_meta']['status'])
