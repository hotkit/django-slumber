from httplib2 import Http
from simplejson import loads

class Client(object):
    def __init__(self, server='localhost', root='', protocol='http'):
        self.protocol = protocol 
        self.server = server
        self.root = root
        self.http = Http()

        self.slumber_test = True 
        self.django_contrib_messages = True

    def _do_get(self, uri, query={}):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """ 
        url = self._get_url(uri) 
        request, content = self.http.request(url)
        return request, loads(content)
        
    def _get_url(self, uri='/'):
        server = self.protocol + '://' + self.server
        return  server + self.root + uri
