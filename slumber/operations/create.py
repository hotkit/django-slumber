"""
    Implements creation of an object.
"""
from slumber.operations import ModelOperation


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
