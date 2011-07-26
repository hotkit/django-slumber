from django.conf import settings
from django.test.client import Client as FakeClient

from httplib2 import Http
from simplejson import loads


def get(ua, url):
    slumber_local = getattr(settings, 'SLUMBER_LOCAL', 'http://localhost:8000/')
    if url.startswith(slumber_local):
        url_fragment = url[len(slumber_local) - 1:]
        response = ua.fake.get(url_fragment,
            HTTP_HOST='localhost:8000')
        if response.status_code in [301, 302]:
            return get(ua, response['location'])
        assert response.status_code == 200, url
        content = response.content
    else:
        response, content = ua.http.request(url)
        assert response.status == 200, url
    return response, loads(content)


class DictObject(object):
    """Allows generic Python objects to be created from a nested dict
    structure describing the attrbutes.
    """

    def __init__(self, **kwargs):
        """Load the specified key values.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)


#def merge_attrs(host, attrs):
    #"""Sets attributes on an object based on values found in a dict in
    #a nested manner.
    #"""
    #for k, v in attrs.items():
        #if hasattr(v, 'items'):
            #if not hasattr(host, k):
                #setattr(host, k, DictObject(**v))
            #else:
                #_merge_attrs(getattr(host, k), v)
        #else:
            #setattr(host, k, v)


class Client(object):
    def __init__(self, server='localhost', root='', protocol='http'):
        self.protocol = protocol
        self.server = server
        self.fake = FakeClient()
        self.http = Http()

        self._load_apps(root)

    def _do_get(self, uri):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """
        url = self._get_url(uri)
        return get(self, url)

    def _get_url(self, uri='/'):
        server = self.protocol + '://' + self.server
        return  server + uri

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
        self._load(url, 'apps', self, self._load_models, MockedModel)

    def _load_models(self, app, url):
        """
        inject attribute app.x where x is a key in models
        the value of x is loaded using _load_model method from models[key]
        """
        self._load(url, 'models', app, self._load_model, DataFetcher)

    def _load_model(self, clz, url):
        clz.http = self.http
        clz.fake = self.fake
        clz.url = self._get_url(url)

class MockedModel(object):
    pass

class DataFetcher(object):
    command = 'data/%s/'

    def get(self, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is None:
            return None
        url = self.url + (self.command % pk)
        response, json = get(self, url)
        obj = MockedModel()
        for field, value in json['fields'].items():
            setattr(obj, field, value['data'])
        return obj

