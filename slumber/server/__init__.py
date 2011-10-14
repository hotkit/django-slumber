"""
    The standard Slumber server implementation.
"""
from django.conf import settings
from django.core.urlresolvers import reverse


def get_slumber_service():
    """Returns the current Slumber service name.

    This allows us to control the setting value in tests more easily for
    early versions of Django.
    """
    return getattr(settings, 'SLUMBER_SERVICE', None)


def get_slumber_root():
    """Returns the location of the Slumber on this server.
    """
    root = reverse('slumber.server.views.service_root')
    service = get_slumber_service()
    if service:
        return '%s%s/' % (root, service)
    else:
        return root
