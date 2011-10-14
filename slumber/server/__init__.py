"""
    The standard Slumber server implementation.
"""
from django.conf import settings
from django.core.urlresolvers import reverse


def get_slumber_root():
    """Returns the location of the Slumber on this server.
    """
    root = reverse('slumber.server.views.service_root')
    service = getattr(settings, 'SLUMBER_SERVICE', None)
    if service:
        return '%s/%s' % (root, service)
    else:
        return root
