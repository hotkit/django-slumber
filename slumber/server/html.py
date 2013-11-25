import collections
from BeautifulSoup import BeautifulSoup
from types import NoneType
from django.http import HttpResponse


def build_html(request, response, content_type):
    dom = BeautifulSoup(convert(response)).prettify()
    return HttpResponse(dom, 'text/HTML', status=response['_meta']['status'])

def convert(obj):
    if type(obj) in (int, float, str, unicode, bool, NoneType):
        return convert_atom(obj)
    if isinstance(obj, dict):
        return convert_dict(obj)
    if type(obj) in (list, set, tuple) or isinstance(obj, collections.Iterable):
        return convert_list(obj)
    raise TypeError('Unsupported data type')

def convert_atom(val):
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
    output = "<dl>"
    for k, v in obj.items():
        output += '<dt>%s</dt>' % k
        output += '<dd>%s</dd>' % convert(v)
    output += "</dl>"
    return output

def convert_list(items):
    output = "<ol>"
    for item in items:
        output += '<li>%s</li>' % convert(item)
    output += "</ol>"
    return output
