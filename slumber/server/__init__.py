"""
    The standard Slumber server implementation.
"""
from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse


def get_slumber_service():
    """Returns the current Slumber service name.

    This allows us to control the setting value in tests more easily for
    early versions of Django.
    """
    return getattr(settings, 'SLUMBER_SERVICE', None)


def get_slumber_directory():
    """Returns the directory setting.

    This allows us to control the setting value in tests more easily for
    early versions of Django.
    """
    return getattr(settings, 'SLUMBER_DIRECTORY',
        'http://localhost:8000/slumber/')


def get_slumber_local_url_prefix():
    """Returns the local URL prefix for Slumber access.
    """
    directory = get_slumber_directory()
    if hasattr(directory, 'items'):
        assert False, "Not implemented"
    parsed = urlparse(directory)
    return '%s://%s/' % (parsed[0], parsed[1])


def get_slumber_services():
    """Returns the slumber services from the directory (if specified)
    """
    directory = get_slumber_directory()
    if hasattr(directory, 'items'): # Feels like a dict
        return directory
    else:
        return None


def get_slumber_root():
    """Returns the location of the Slumber on this server.
    """
    root = reverse('slumber.server.views.service_root')
    service = get_slumber_service()
    if service:
        return '%s%s/' % (root, service)
    else:
        return root
