"""
    Integration between Slumber and Django models.
"""
from django.db.models import URLField, SubfieldBase

from slumber.scheme import to_slumber_scheme
from slumber.server import get_slumber_services


class RemoteForeignKey(URLField):
    """Wraps Django's URLField to provide a field that references a remote
    object on another Slumber service.
    """
    # Django already has too many public methods and we can't change it
    # pylint: disable=R0904

    description = "A Slumber object on another service."
    __metaclass__ = SubfieldBase

    def __init__(self, service, **kwargs):
        self.service = service
        super(RemoteForeignKey, self).__init__(**kwargs)

    def get_db_prep_value(self, value, *a, **kw):
        return super(RemoteForeignKey, self).get_db_prep_value(
            to_slumber_scheme(value, self.service,
            get_slumber_services()))
