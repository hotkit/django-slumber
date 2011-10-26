"""
    The standard Slumber server implementation.
"""
from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse


class AbsoluteURIRequired(Exception):
    """Thrown when the local service is configured with a relative URL.
    """
    pass

class NoServiceSpecified(Exception):
    """Thrown when the service option for SLUMBER_DIRECTORY is used
    but no SLUMBER_SERVICE has been given.
    """
    pass


def _get_slumber_service():
    """Implementation for get_slumber_service which allows a single
    patching point.
    """
    return getattr(settings, 'SLUMBER_SERVICE', None)
def get_slumber_service():
    """Returns the current Slumber service name.

    This allows us to control the setting value in tests more easily for
    early versions of Django.
    """
    return _get_slumber_service()


def _get_slumber_directory():
    """Implementation for get_slumber_directory which allows a single
    patching point.
    """
    return getattr(settings, 'SLUMBER_DIRECTORY',
        'http://localhost:8000/slumber/')
def get_slumber_directory():
    """Returns the directory setting.

    This allows us to control the setting value in tests more easily for
    early versions of Django.
    """
    return _get_slumber_directory()


def get_slumber_local_url_prefix():
    """Returns the local URL prefix for Slumber access.
    """
    directory = get_slumber_directory()
    if hasattr(directory, 'items'):
        try:
            directory = directory[get_slumber_service()]
        except KeyError:
            raise NoServiceSpecified("If you have a Slumber directory "
                "specifying services you must also set SLUMBER_SERVICE")
    parsed = urlparse(directory)
    scheme, netloc = parsed[0], parsed[1]
    if not scheme or not netloc:
        raise AbsoluteURIRequired("The URL for the local service must be "
        "specified as absolute: %s is currently %s" %
            (get_slumber_service(), directory))
    return '%s://%s/' % (parsed[0], parsed[1])


def get_slumber_services(directory = None):
    """Returns the slumber services from the directory (if specified)
    """
    if not directory:
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
