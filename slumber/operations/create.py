"""
    Implements creation of an object.
"""
from slumber.operations import ModelOperation
from slumber.operations.instancedata import instance_data
from slumber.server.http import require_permission


class CreateInstance(ModelOperation):
    """Allows for the creation of new instances.
    """
    def post(self, request, response, appname, modelname):
        """Perform the object creation.
        """
        @require_permission('%s.add_%s' % (appname, modelname.lower()))
        def do_create(_cls, request):
            """Use an inner function so that we can generate a proper
            permission name at run time.
            """
            instance = self.model.model(**dict([(k, v)
                for k, v in request.POST.items()]))
            instance.save()
            return instance_data(response, self.model, instance)
        return do_create(self, request)

