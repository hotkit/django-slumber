"""
    Code for the Slumber client connector.
"""
import logging
from urllib import urlencode
from urlparse import urljoin

from django.conf import settings

from slumber._caches import MODEL_URL_TO_SLUMBER_MODEL, PER_THREAD
from slumber.connector.api import get_model
from slumber.connector.dictobject import DictObject
from slumber.connector.json import from_json_data
from slumber.connector.ua import get
from slumber.server import get_slumber_service, get_slumber_directory, \
    get_slumber_services, get_slumber_local_url_prefix, get_slumber_root


def _get_slumber_authn_name():
    """Used in the implementation of get_auth_name so it can be easily
    patched.
    """
    return getattr(settings, 'SLUMBER_AUTHN_NAME', get_slumber_service())
def get_slumber_authn_name():
    """Return the user name that is to be used for authenticating Slumber
    requests to the back end. This user name is used together with the
    SECRET_KEY and defaults to the service name.
    """
    return _get_slumber_authn_name()


class ServiceConnector(object):
    """Connects to a service.
    """
    def __init__(self, directory):
        self._directory = directory

    def __getattr__(self, attr_name):
        """Fetch the application list from the Slumber directory on request.
        """
        logging.debug("Looking for attribute %s on %s for directory %s",
            attr_name, self, self._directory)
        if not self._directory:
            logging.debug("Raising AttributeError as _directory is falsey")
            raise AttributeError(attr_name)
        _, json = get(self._directory)
        logging.debug(
            "Looking for attribute %s on %s resulted in these applications %s",
            attr_name, self, json)
        # Pylint gets confused by the JSON object
        # pylint: disable=E1103
        json_apps = json.get('apps', {})
        apps = {}
        for app in json_apps.keys():
            root = apps
            for k in app.split('.'):
                if not root.has_key(k):
                    root[k] = {}
                root = root[k]
        def recurse_apps(loc, this_level, name):
            """Recursively build the application connectors.
            """
            current_appname = '.'.join(name)
            if json_apps.has_key(current_appname):
                loc._directory = urljoin(self._directory,
                    json_apps[current_appname])
            for k, v in this_level.items():
                app_cnx = ServiceConnector(None)
                setattr(loc, k, app_cnx)
                recurse_apps(app_cnx, v, name + [k])
        recurse_apps(self, apps, [])
        models = json.get('models', {})
        for model_name, url in models.items():
            model_url = urljoin(self._directory, url)
            model = get_model(model_url)
            setattr(self, model_name, model)
        if attr_name in models.keys():
            return getattr(self, attr_name)
        elif attr_name in apps.keys():
            return getattr(self, attr_name)
        else:
            raise AttributeError(attr_name, json)


class Client(ServiceConnector):
    """The first level of the Slumber client connector.
    """
    def __init__(self, directory=None):
        self._instances = []
        client_apps = getattr(settings, 'SLUMBER_CLIENT_APPS', [])
        for app in client_apps:
            __import__(app, globals(), locals(), ['slumber_client'])
        services = get_slumber_services(directory)
        if not services:
            if not directory:
                directory = get_slumber_directory()
            super(Client, self).__init__(directory)
        else:
            for k, v in services.items():
                setattr(self, k, ServiceConnector(v))
            super(Client, self).__init__(None)

    @classmethod
    def _flush_client_instance_cache(cls):
        """Flush the (global) instance cache.
        """
        if getattr(PER_THREAD, 'cache', None):
            PER_THREAD.cache.clear()
