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


class CreateInstance(ModelOperation):
    """Allows for the creation of new instances.
    """
    def operation(self, request, response, _appname, _modelname):
        """Perform the object creation.
        """
        if request.method == 'POST':
            response['created'] = True
            instance = self.model.model(**dict([(k, str(v))
                for k, v in request.POST.items()]))
            instance.save()
            response['pk'] = instance.pk
        else:
            response['created'] = False
