from django.conf import settings
from django.test.client import Client as FakeClient

from urlparse import urljoin

from httplib2 import Http
from simplejson import loads

from slumber.json import from_json_data


_fake = FakeClient()
_http = Http()


class DictObject(object):
    """Allows generic Python objects to be created from a nested dict
    structure describing the attrbutes.
    """

    def __init__(self, **kwargs):
        """Load the specified key values.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

class LazyDictObject(DictObject):
    """Allows generic Python objects to be created lazily when attributes are requested.
    """
    def __init__(self, getattr_function, **kwargs):
        self._getattr = getattr_function
        super(LazyDictObject, self).__init__(**kwargs)

    def __getattr__(self, name):
        return self._getattr(self, name)


def get(url, query={}):
    slumber_local = getattr(settings, 'SLUMBER_LOCAL', 'http://localhost:8000/')
    if url.startswith(slumber_local):
        url_fragment = url[len(slumber_local) - 1:]
        response = _fake.get(url_fragment, query,
            HTTP_HOST='localhost:8000')
        if response.status_code in [301, 302]:
            return get(response['location'])
        assert response.status_code == 200, (url_fragment, response)
        content = response.content
    else:
        assert not query # Not implemented for remote end yet
        response, content = _http.request(url)
        assert response.status == 200, url
    return response, loads(content)


class Client(object):
    def __init__(self, directory=None):
        if not directory:
            directory = getattr(settings, 'SLUMBER_DIRECTORY',
                'http://localhost:8000/slumber/')
        self._directory = directory
        self._load_apps(directory)

    def _do_get(self, uri):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """
        url = self._get_url(uri)
        return get(url)

    def _get_url(self, uri='/'):
        return urljoin(self._directory, uri)

    def _load(self, url, type, obj, sub_fn, cls, *cls_args):
        """
        1. make a GET request to the given `url`
        2. get a dict of json.parse(content)[type] (i.e. 'apps', 'models')
        3. inject attributes into obj, for each key in the dict
        4. use the given `sub_fn` to recursively load the url in the value and set it as a result of each attribute
        """
        response, json = self._do_get(url)
        response_dict = json[type]

        for key, value in response_dict.items():
            key = key.replace('.', '_')
            attribute_value = cls(*cls_args)
            setattr(obj, key, attribute_value)
            sub_fn(attribute_value, value)

    def _load_apps(self, url):
        """
        inject attribute self.x where x is a key in apps
        the value of x is loaded using _load_models method from apps[key]
        """
        self._load(url, 'apps', self, self._load_models, DictObject)

    def _load_models(self, app, url):
        """
        inject attribute app.x where x is a key in models
        the value of x is loaded using _load_model method from models[key]
        """
        self._load(url, 'models', app, self._load_model, DataFetcher)

    def _load_model(self, clz, url):
        clz.url = self._get_url(url)


class DataFetcher(object):
    def get(self, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is None:
            return None
        url = self.url + 'get/'
        response, json = get(url, {'pk': pk})
        def get_data_array(obj, name):
            if name in json['data_arrays'].keys():
                return []
            else:
                raise AttributeError(name)
        obj = LazyDictObject(get_data_array,
            **dict([(k, from_json_data(j)) for k, j in json['fields'].items()]))
        return obj
