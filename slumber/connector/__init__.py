"""
    Code for the Slumber client connector.
"""
from django.conf import settings

from urllib import urlencode
from urlparse import urljoin

from slumber.connector.dictobject import DictObject, LazyDictObject
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


def _return_data_array(base_url, arrays, _, name):
    """Implement the lazy fetching of the instance data.
    """
    # Pylint makes a bad type deduction
    # pylint: disable=E1103
    if name in arrays.keys():
        data_array = []
        _, data = get(urljoin(base_url, arrays[name]))
        while True:
            for obj in data['page']:
                data_array.append(
                    InstanceConnector(
                        urljoin(base_url, obj['data']), obj['display']))
            if data.has_key('next_page'):
                _, data = get(urljoin(base_url, data['next_page']))
            else:
                break
        return data_array
    else:
        raise AttributeError(name)

class ModelConnector(DictObject):
    """Handles the connection to a Django model.
    """
    def __init__(self, url, **kwargs):
        self._url = url
        super(ModelConnector, self).__init__(**kwargs)

    def __getattr__(self, name):
        attrs = ['name', 'module']
        if name in attrs:
            _, json = get(self._url)
            for attr in attrs:
                setattr(self, attr, json[attr])
            return getattr(self, name)
        else:
            raise AttributeError(name)

    def get(self, **kwargs):
        """Implements the client side for the model 'get' operator.
        """
        assert len(kwargs), \
            "You must supply kwargs to filter on to fetch the instance"
        url = urljoin(self._url, 'get/')
        _, json = get(url + '?' + urlencode(kwargs))
        def get_data_array(obj, name):
            """Implement simple partial application using a closure.
            """
            return _return_data_array(self._url, json['data_arrays'], obj, name)
        instance_type = type(self.module + '.' + self.name,
            (LazyDictObject,), {})
        obj = instance_type(get_data_array,
            **dict([(k, from_json_data(self._url, j))
                for k, j in json['fields'].items()]))
        return obj


class InstanceConnector(DictObject):
    """Connects to a remote instance.
    """
    def __init__(self, url, display, **kwargs):
        self._url = url
        self._unicode = display
        super(InstanceConnector, self).__init__(**kwargs)

    def __unicode__(self):
        return self._unicode

    def __getattr__(self, name):
        _, json = get(self._url)
        for k, v in json['fields'].items():
            setattr(self, k, from_json_data(self._url, v))
        if name in json['fields'].keys():
            return getattr(self, name)
        return _return_data_array(self._url, json['data_arrays'], self, name)
