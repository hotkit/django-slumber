from httplib2 import Http
from simplejson import loads

class Client(object):
    def __init__(self, server='localhost', root='', protocol='http'):
        self.protocol = protocol 
        self.server = server
        self.root = root
        self.slumber_test = True 
        self.django_contrib_messages = True
        self.http = Http()

    def _do_get(self, uri='/', query={}):
        """
        get response in JSON format from slumber server and loads it into a python dict
        """ 
        url = self.protocol + '://' + self.server + self.root + uri
        request, content = self.http.request(url)
        return request, loads(content)
        
