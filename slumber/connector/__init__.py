"""
    Code for the Slumber client connector.
"""
from django.conf import settings

from urllib import urlencode
from urlparse import urljoin

from slumber.connector.dictobject import DictObject
from slumber.connector.model import ModelConnector
from slumber.connector.ua import get
from slumber.json import from_json_data


class Client(object):
    """The first level of the Slumber client connector.
    """
    def __init__(self, directory=None):
        if not directory:
            directory = getattr(settings, 'SLUMBER_DIRECTORY',
                'http://localhost:8000/slumber/')
        self._directory = directory

    def __getattr__(self, attr_name):
        """Fetch the application list from the Slumber directory on request.
        """
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


class AppConnector(DictObject):
    """Handles the client connection to a Django application.
    """
    _url = None
    def __getattr__(self, name):
        if not self._url:
            raise AttributeError(name)
        _, json = get(self._url)
        models = json['models']
        for model, url in models.items():
            model_url = urljoin(self._url, url)
            setattr(self, model, ModelConnector(model_url))
        if name in models.keys():
            return getattr(self, name)
        else:
            raise AttributeError(name)
