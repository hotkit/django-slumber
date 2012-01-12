"""
    Wrappers for interacting with Django in the server.
"""
from django.conf import settings

from slumber._caches import APP_FROM_APPNAME
from slumber.server.application import DjangoApp


def applications():
    """Return the Django application wrappers for all installed apps.
    """
    if APP_FROM_APPNAME:
        return APP_FROM_APPNAME.values()
    else:
        apps = [get_application(app) for app in settings.INSTALLED_APPS]
        for app in apps:
            __import__(app.name, globals(), locals(), ['slumber_config'])
        return apps

def get_application(app_name):
    """Build a Django application wrapper around an application given
    by its name.
    """
    if not APP_FROM_APPNAME.has_key(app_name):
        APP_FROM_APPNAME[app_name] = DjangoApp(app_name)
    return APP_FROM_APPNAME[app_name]
