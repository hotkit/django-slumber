"""
    The standard Slumber server implementation.
"""
from django.core.urlresolvers import reverse


def get_slumber_root():
    """Returns the location of the Slumber on this server.
    """
    return reverse('slumber.server.views.get_applications')
