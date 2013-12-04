"""
    Allows the data URL to be found for a given object.
"""
from django.http import HttpResponseNotFound

from slumber.operations import ModelOperation
from slumber.operations.instancedata import instance_data
from slumber.server.http import require_user


class DereferenceInstance(ModelOperation):
    """Given a primary key (or other unique set of attributes) redirects
    to the instance item.
    """
    @require_user
    def get(self, request, response, _appname, _modelname):
        """Work out the correct data URL for an instance we're going to
        search for.
        """
        try:
            instance = self.model.model.objects.get(
                **dict([(k, request.GET[k])
                    for k in request.GET.keys()]))
            return instance_data(response, self.model, instance)
        except self.model.model.DoesNotExist:
            return HttpResponseNotFound()
