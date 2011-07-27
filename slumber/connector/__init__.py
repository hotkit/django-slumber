from django.conf import settings

from urllib import urlencode
from urlparse import urljoin

from slumber.connector.dictobject import DictObject, LazyDictObject
from slumber.connector.ua import get
from slumber.json import from_json_data


class Client(object):
    def __init__(self, directory=None):
        if not directory:
            directory = getattr(settings, 'SLUMBER_DIRECTORY',
                'http://localhost:8000/slumber/')
        self._directory = directory

    def __getattr__(self, attr_name):
        response, json = get(self._directory)
        apps = {}
        for app in json['apps'].keys():
            root = apps
            for k in app.split('.'):
                if not root.has_key(k):
                    root[k] = {}
                root = root[k]
        def recurse_apps(loc, this_level, name):
            current_appname = '.'.join(name)
            if json['apps'].has_key(current_appname):
                loc._url = urljoin(self._directory, json['apps'][current_appname])
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
    _url = None
    def __getattr__(self, name):
        if not self._url:
            raise AttributeError(name)
        response, json = get(self._url)
        models = json['models']
        for m, u in models.items():
            model_url = urljoin(self._url, u)
            setattr(self, m, ModelConnector(model_url))
        if name in models.keys():
            # We are not yet lazy loading the models so this line won't be
            # in test coverage
            return getattr(self, name)
        else:
            raise AttributeError(name)


def _return_data_array(base_url, arrays, instance, name):
    if name in arrays.keys():
        data_array = []
        response, data = get(urljoin(base_url, arrays[name]))
        while True:
            for obj in data['page']:
                data_array.append(
                    InstanceConnector(
                        urljoin(base_url, obj['data']), obj['display']))
            if data.has_key('next_page'):
                response, data = get(urljoin(base_url, data['next_page']))
            else:
                break
        return data_array
    else:
        raise AttributeError(name)

class ModelConnector(DictObject):
    def __init__(self, url):
        self._url = url

    def get(self, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is None:
            return None
        url = urljoin(self._url, 'get/')
        response, json = get(url + '?' + urlencode({'pk': pk}))
        def get_data_array(obj, name):
            return _return_data_array(self._url, json['data_arrays'], obj, name)
        obj = LazyDictObject(get_data_array,
            **dict([(k, from_json_data(self._url, j)) for k, j in json['fields'].items()]))
        return obj


class InstanceConnector(DictObject):
    def __init__(self, url, display, **kwargs):
        self._url = url
        self._unicode = display
        super(InstanceConnector, self).__init__(**kwargs)

    def __unicode__(self):
        return self._unicode

    def __getattr__(self, name):
        response, json = get(self._url)
        for k, v in json['fields'].items():
            setattr(self, k, from_json_data(self._url, v))
        if name in json['fields'].keys():
            return getattr(self, name)
        return _return_data_array(self._url, json['data_arrays'], self, name)
