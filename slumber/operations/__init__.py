"""
    Implements the server side operations on models and instances.
"""
from django.core.urlresolvers import reverse


class ModelOperation(object):
    """Base class for model operations.
    """
    model_operation = True
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.regex = ''
        self.path = model.path + name + '/'

    def forbidden(self, request, response, *_):
        """Return an error to say that the method type is not allowed.
        """
        response['_meta']['status'] = 403

    def operation(self, request, response, *args):
        """Perform the requested operation in the server.
        """
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            getattr(self, request.method.lower(), self.forbidden)(request, response, *args)
        else:
            self.forbidden(request, response)


class InstanceOperation(ModelOperation):
    """Base class for operations on instances.
    """
    model_operation = False
    def __init__(self, model, name):
        super(InstanceOperation, self).__init__(model, name)
        self.regex = '([^/]+)/'
