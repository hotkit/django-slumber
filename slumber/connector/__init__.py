from django.conf import settings

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
        self._load_apps(directory)

    def _do_get(self, uri):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """
        url = self._get_url(uri)
        return get(url)

    def _get_url(self, uri='/'):
        return urljoin(self._directory, uri)

    def _load(self, url, type, obj, sub_fn, cls):
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
            attribute_value = cls()
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
        self._load(url, 'models', app, self._load_model, ModelConnector)

    def _load_model(self, clz, url):
        clz.url = self._get_url(url)


class ModelConnector(DictObject):
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
