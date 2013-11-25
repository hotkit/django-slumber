"""Implements the conversion of the response data to valid html data.
"""

import collections
from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse
from types import NoneType


def build_html(request, response, content_type):
    """Return http response object in text/html format.
    """
    html_template = '<!DOCTYPE HTML><html><body>%s</body></html>'
    dom = html_template % convert(response)
    if settings.DEBUG:
        dom = BeautifulSoup(dom).prettify()

    return HttpResponse(dom, 'text/HTML', status=response['_meta']['status'])

def convert(obj):
    """This is the recursively converter.
    """
    if type(obj) in (int, float, str, unicode, bool, NoneType):
        return convert_atom(obj)
    if isinstance(obj, dict):
        return convert_dict(obj)
    if type(obj) in (list, set, tuple) or isinstance(obj, collections.Iterable):
        return convert_list(obj)
    raise TypeError('Unsupported data type')

def convert_atom(val):
    """Return xml element for atom which are 'int', 'float',
    'long', 'string', 'boolean' and 'null'.
    """
    if type(val) is int:
        val_type = "int"
    elif type(val) is float:
        val_type = "float"
    elif type(val) in (str, unicode):
        val_type = "string"
    elif type(val) is bool:
        val_type = "boolean"
    elif type(val) is NoneType:
        val_type = "null"
        val = ""
    else:
        raise TypeError('Unsupported data type')
    return '<span class="%s">%s</span>' % (val_type, val)

def convert_dict(obj):
    """Return xml element for dict.
    """
    output = "<dl>"
    for k, v in obj.items():
        output += '<dt>%s</dt>' % k
        output += '<dd>%s</dd>' % convert(v)
    output += "</dl>"
    return output

def convert_list(items):
    """Return xml element for list.
    """
    output = "<ol>"
    for item in items:
        output += '<li>%s</li>' % convert(item)
    output += "</ol>"
    return output
