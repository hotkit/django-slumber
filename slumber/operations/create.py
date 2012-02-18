"""
    Implements creation of an object.
"""
from slumber.operations import ModelOperation
from slumber.operations.instancedata import instance_data


class CreateInstance(ModelOperation):
    """Allows for the creation of new instances.
    """
    def post(self, request, response, _appname, _modelname):
        """Perform the object creation.
        """
        instance = self.model.model(**dict([(k, str(v))
            for k, v in request.POST.items()]))
        instance.save()
        return instance_data(request, response, self.model, instance)
