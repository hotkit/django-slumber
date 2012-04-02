"""
    Implements the server side operations on models and instances.
"""
from django.core.urlresolvers import reverse


def _forbidden(_request, response, *_):
    """Return an error to say that the method type is not allowed.
    """
    response['_meta']['status'] = 405
    response['_meta']['message'] = "Method Not Allowed"


class ModelOperation(object):
    """Base class for model operations.
    """
    METHODS = ['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE']
    model_operation = True
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.regex = ''
        self.path = model.path + name + '/'

    def headers(self, retvalue, request, response):
        """Calculate and place extra headers needed for certain types of
        response.
        """
        if response['_meta']['status'] == 405 or request.method == 'OPTIONS':
            response['_meta'].setdefault('headers', {})
            response['_meta']['headers']['Allow'] = \
                ', '.join([method
                    for method in self.METHODS
                        if hasattr(self, method.lower())])
        return retvalue


    def operation(self, request, response, *args):
        """Perform the requested operation in the server.
        """
        if request.method in self.METHODS:
            retvalue = getattr(self, request.method.lower(), _forbidden)(
                request, response, *args)
            return self.headers(retvalue, request, response)
        else:
            _forbidden(request, response)
        return self.headers(None, request, response)


    def options(self, request, response, *_):
        """A standard options response that will fill in the Allow header.
        """
        return self.headers(None, request, response)


class InstanceOperation(ModelOperation):
    """Base class for operations on instances.
    """
    model_operation = False
    def __init__(self, model, name):
        super(InstanceOperation, self).__init__(model, name)
        self.regex = '([^/]+)/'
