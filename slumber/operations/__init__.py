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


class InstanceOperation(ModelOperation):
    """Base class for operations on instances.
    """
    model_operation = False
    def __init__(self, model, name):
        super(InstanceOperation, self).__init__(model, name)
        self.regex = '([^/]+)/'
