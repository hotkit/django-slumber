"""
    Implements the JSON formatting for both the server.
"""
from django.core.urlresolvers import reverse

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL


DATA_MAPPING = {
        'django.db.models.fields.AutoField': lambda m, i, fm, v: v,
        'django.db.models.fields.BooleanField': lambda m, i, fm, v: v,
        'django.db.models.fields.related.ForeignKey':
            lambda m, i, fm, v: v.pk if v else None,
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
            root = reverse('slumber.server.views.get_applications')
            return dict(type=root + rel_to.path,
                display=unicode(value),
                data = root + rel_to.path + 'data/%s/' % value.pk)
    elif DATA_MAPPING.has_key(fieldmeta['type']):
        return DATA_MAPPING[fieldmeta['type']](
            model, instance, fieldmeta, value)
    else:
        if value is None:
            return None
        else:
            return unicode(value)
