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
        response, json = get(self._directory)
        def set_app_attr(on, app_url, *path):
            if len(path) == 0:
                on._url = app_url
                return
            elif not hasattr(on, path[0]):
                setattr(on, path[0], AppConnector())
            set_app_attr(getattr(on, path[0]), app_url, *path[1:])
        for app, url in json['apps'].items():
            app_url = urljoin(self._directory, url)
            set_app_attr(self, app_url, *app.split('.'))


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
            if name in json['data_arrays'].keys():
                data_array = []
                response, data = get(urljoin(self._url, json['data_arrays'][name]))
                while len(data['page']):
                    for obj in data['page']:
                        data_array.append(InstanceConnector(obj['data'], obj['display']))
                    if data.has_key('next_page'):
                        response, data = get(urljoin(self._url, data['next_page']))
                    else:
                        break
                return data_array
            else:
                raise AttributeError(name)
        obj = LazyDictObject(get_data_array,
            **dict([(k, from_json_data(j)) for k, j in json['fields'].items()]))
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
