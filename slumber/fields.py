"""
    Integration between Slumber and Django models.
"""
from django.db.models import URLField, SubfieldBase

from slumber.connector.api import _InstanceProxy, get_instance
from slumber.connector.dictobject import DictObject
from slumber.forms import RemoteForeignKeyField
from slumber.scheme import to_slumber_scheme, from_slumber_scheme
from slumber.server import get_slumber_services


class RemoteForeignKey(URLField):
    """Wraps Django's URLField to provide a field that references a remote
    object on another Slumber service.
    """
    # Django already has too many public methods and we can't change it
    # pylint: disable=R0904

    description = "A remote Slumber object."
    __metaclass__ = SubfieldBase

    def __init__(self, model_url, **kwargs):
        self.model_url = model_url
        super(RemoteForeignKey, self).__init__(**kwargs)

    def run_validators(self, value):
        # Do not rely on validators as we want to support Django 1.0
        pass

    def get_db_prep_value(self, value, *a, **kw):
        if isinstance(value, basestring):
            url = to_slumber_scheme(value, get_slumber_services())
        else:
            url = to_slumber_scheme(value._url, get_slumber_services())
        return super(RemoteForeignKey, self).get_db_prep_value(url, *a, **kw)

    def get_prep_value(self, value, *a, **kw):
        if isinstance(value, basestring) or isinstance(value, DictObject):
            return value
        url = to_slumber_scheme(value._url, get_slumber_services())
        return super(RemoteForeignKey, self).get_prep_value(url, *a, **kw)

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, _InstanceProxy):
            return value
        instance_url = from_slumber_scheme(
            super(RemoteForeignKey, self).to_python(value),
            get_slumber_services())
        model_url = from_slumber_scheme(
            self.model_url, get_slumber_services())
        return get_instance(model_url, instance_url, None)

    def formfield(self, **kwargs):
        defaults = {'form_class': RemoteForeignKeyField,
            'model_url': self.model_url}
        defaults.update(kwargs)
        return super(RemoteForeignKey, self).formfield(**defaults)

