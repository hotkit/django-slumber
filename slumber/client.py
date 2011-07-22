from httplib2 import Http
from simplejson import loads

class Client(object):
    def __init__(self, server='localhost', root='', protocol='http'):
        self.protocol = protocol 
        self.server = server
        self.http = Http()

        self._load_apps(root)

    def _do_get(self, uri, query={}):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """ 
        url = self._get_url(uri) 
        print 'url = ', url
        request, content = self.http.request(url)
        return request, loads(content)
        
    def _get_url(self, uri='/'):
        server = self.protocol + '://' + self.server
        return  server + uri

    def _load_apps(self, url):
        print 'in _load_apps'
        response, json = self._do_get(url)
        apps = json['apps']

        for key, value in apps.items():
            models_url = value
            field_name = key.replace('.', '_')
            setattr(self, field_name, MockedModel())
            self._load_models(getattr(self, field_name), models_url)
        print 'exit _load_apps'

    def _load_models(self, app, url):
        print 'in _load_models'
        response, json = self._do_get(url)
        models = json['models']
        
        for key, value in models.items():
            model_url = value
            field_name = key.replace('.', '_')
            setattr(app, field_name, value)

        print 'exit _load_models'

class MockedModel(object):
    pass
