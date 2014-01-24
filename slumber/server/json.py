"""
    Implements the JSON formatting for the server.
"""
from simplejson import dumps, JSONEncoder

from django.http import HttpResponse
from django.conf import settings

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.server import get_slumber_root


DATA_MAPPING = {
        'django.db.models.fields.AutoField': lambda m, i, fm, v: v,
        'django.db.models.fields.BooleanField': lambda m, i, fm, v: v,
        'django.db.models.fields.NullBooleanField': lambda m, i, fm, v: v,
    }


def to_json_data(model, instance, fieldname, fieldmeta):
    """Convert a model field to JSON on the server.
    """
    value = getattr(instance, fieldname)
    if fieldmeta['kind'] == 'object':
        if value is None:
            return None
        else:
            rel_to = DJANGO_MODEL_TO_SLUMBER_MODEL[type(value)]
            root = get_slumber_root()
            return dict(type=root + rel_to.path,
                display=unicode(value),
                data = root + rel_to.path + 'data/%s/' % value.pk)
    elif DATA_MAPPING.has_key(fieldmeta['type']):
        func = DATA_MAPPING[fieldmeta['type']]
        return func(model, instance, fieldmeta, value)
    else:
        if value is None:
            return None
        else:
            return unicode(value)


class _proxyEncoder(JSONEncoder):
    """If we don't know how to deal with the attribute type we'll just
    convert to a string and hope that's ok for now.
    """
    # An attribute inherited from JSONEncoder hide this method
    # pylint: disable=E0202
    def default(self, obj):
        return unicode(obj)


def as_json(_request, response, content_type):
    """Implement the default accept handling which will return JSON data.
    """
    response_root = getattr(response, 'root', None)
    if response_root:
        to_dump = response[response.root]
    else:
        to_dump = response
    if settings.DEBUG:
        dump_content = dumps(
            to_dump, indent=4,
            cls=_proxyEncoder)
    else:
        dump_content = dumps(
            to_dump, cls=_proxyEncoder)

    return HttpResponse(
        dump_content, content_type or 'text/plain',
        status=response['_meta']['status'])

