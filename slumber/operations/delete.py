"""
    Implements creation of an object.
"""
from slumber.operations import InstanceOperation


class DeleteInstance(InstanceOperation):
    """Allows for the removal of instances.
    """
    def post(self, _request, response, _appname, _modelname, pk):
        """Perform the object deletion.
        """
        instance = self.model.model.objects.get(pk=pk)
        instance.delete()
        response['deleted'] = True
