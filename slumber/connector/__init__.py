"""
    Code for the Slumber client connector.
"""
from django.conf import settings

from urllib import urlencode
from urlparse import urljoin

from slumber._caches import CLIENT_INSTANCE_CACHE, \
    MODEL_URL_TO_SLUMBER_MODEL
from slumber.connector.api import get_model
from slumber.connector.dictobject import DictObject
from slumber.connector.json import from_json_data
from slumber.connector.ua import get
from slumber.server import get_slumber_service, get_slumber_directory, \
    get_slumber_services


class ServiceConnector(object):
    """Connects to a service.
    """
    def __init__(self, directory):
        self._directory = directory

    def __getattr__(self, attr_name):
        """Fetch the application list from the Slumber directory on request.
        """
        if not self._directory:
            raise AttributeError(attr_name)
        _, json = get(self._directory)
        apps = {}
        for app in json['apps'].keys():
            root = apps
            for k in app.split('.'):
                if not root.has_key(k):
                    root[k] = {}
                root = root[k]
        def recurse_apps(loc, this_level, name):
            """Recursively build the application connectors.
            """
            current_appname = '.'.join(name)
            if json['apps'].has_key(current_appname):
                loc._url = urljoin(self._directory,
                    json['apps'][current_appname])
            for k, v in this_level.items():
                app_cnx = AppConnector()
                setattr(loc, k, app_cnx)
                recurse_apps(app_cnx, v, name + [k])
        recurse_apps(self, apps, [])
        if attr_name in apps.keys():
            return getattr(self, attr_name)
        else:
            raise AttributeError(attr_name)


class Client(ServiceConnector):
    """The first level of the Slumber client connector.
    """
    def __init__(self, directory=None):
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
        CLIENT_INSTANCE_CACHE.clear()


class AppConnector(DictObject):
    """Handles the client connection to a Django application.
    """
    _url = None
    def __getattr__(self, name):
        if not self._url:
            raise AttributeError(name)
        _, json = get(self._url)
        models = json['models']
        for model_name, url in models.items():
            model_url = urljoin(self._url, url)
            model = get_model(model_url)
            setattr(self, model_name, model)
        if name in models.keys():
            return getattr(self, name)
        else:
            raise AttributeError(name)
