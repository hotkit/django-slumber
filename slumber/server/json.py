"""
    Implements the JSON formatting for both the server.
"""
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.server import get_slumber_root


DATA_MAPPING = {
        'django.db.models.fields.AutoField': lambda r, m, i, fm, v: v,
        'django.db.models.fields.BooleanField': lambda r, m, i, fm, v: v,
    }


def to_json_data(request, model, instance, fieldname, fieldmeta):
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
        return DATA_MAPPING[fieldmeta['type']](
            request, model, instance, fieldmeta, value)
    else:
        if value is None:
            return None
        else:
            return unicode(value)
