"""
    Implements creation of an object.
"""
from slumber.operations import InstanceOperation
from slumber.server.http import require_permission


class DeleteInstance(InstanceOperation):
    """Allows for the removal of instances.
    """
    def post(self, request, response, appname, modelname, pk):
        """Perform the object deletion.
        """
        # We need all of these arguments as they are all used
        # pylint: disable=R0913
        @require_permission('%s.delete_%s' % (appname, modelname.lower()))
        def do_delete(_cls, _request):
            """This inner function is used to allow us to build a correct
            permission name at run time based on the application and model
            names.
            """
            instance = self.model.model.objects.get(pk=pk)
            instance.delete()
            response['deleted'] = True
        return do_delete(self, request)

