from httplib2 import Http
from simplejson import loads

class Client(object):
    def __init__(self, server='localhost', root='', protocol='http'):
        self.protocol = protocol 
        self.server = server
        self.http = Http()

        self._load_apps(root)

    def _do_get(self, uri):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """ 
        url = self._get_url(uri) 
        return get(self.http, url) 
        
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
        clz.url = self._get_url(url)
        
def get(http, url):
    response, content = http.request(url)
    assert response.status == 200, url
    return response, loads(content)
 
class MockedModel(object):
    pass

class DataFetcher(object):
    command = 'data/%s/'

    def get(self, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is None:
            return None
        url = self.url + (self.command % pk)
        response, json = get(self.http, url)
        obj = MockedModel()
        for field, value in json['fields'].items():
            setattr(obj, field, value['data'])
        return obj

