"""
    Integration between Slumber and Django models.
"""
from django.db.models import URLField, SubfieldBase

from slumber.connector.api import _InstanceProxy, get_instance_from_url
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

    def get_db_prep_value(self, value, *a, **kw):
        if isinstance(value, basestring):
            return value
        url = value._url
        print "get_db_prep_value", value, url
        final_url = super(RemoteForeignKey, self).get_db_prep_value(
            to_slumber_scheme(url, get_slumber_services()), *a, **kw)
        print "get_db_prep_value", value, final_url
        return final_url

    def get_prep_value(self, value):
        print "get_prep_value", value
        return self.get_db_prep_value(value)

    def to_python(self, value):
        print "to_python", value
        if isinstance(value, _InstanceProxy):
            return value
        url = from_slumber_scheme(
            super(RemoteForeignKey, self).to_python(value),
            get_slumber_services())
        print "to_python", value, url
        return get_instance_from_url(url)
