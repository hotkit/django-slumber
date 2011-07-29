"""
    Wrappers for interacting with Django in the server.
"""
from django.conf import settings

from slumber.application import DjangoApp


def applications():
    """Return the Django application wrappers for all installed apps.
    """
    return [get_application(app) for app in settings.INSTALLED_APPS]


def get_application(app_name):
    """Build a Django application wrapper around an application given
    by its name.
    """
    return DjangoApp(app_name)
