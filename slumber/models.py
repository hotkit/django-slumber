"""
    Integration between Slumber and Django models.
"""
from django.db.models import URLField


class RemoteForeignKey(URLField):
    """Wraps Django's URLField to provide a field that references a remote
    object on another Slumber service.
    """
    # Django already has too many public methods and we can't change it
    # pylint: disable=R0904
    def __init__(self, service, **kwargs):
        self.service = service
        super(RemoteForeignKey, self).__init__(**kwargs)
