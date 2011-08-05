"""
    Allows the data URL to be found for a given object.
"""
from django.http import HttpResponseRedirect

from slumber.operations import ModelOperation
from slumber.server import get_slumber_root


class DereferenceInstance(ModelOperation):
    """Given a primary key (or other unique set of attributes) redirects
    to the instance item.
    """
    def operation(self, request, _response, _appname, _modelname):
        """Work out the correct data URL for an instance we're going to
        search for.
        """
        root = get_slumber_root()
        instance = self.model.model.objects.get(pk=request.GET['pk'])
        return HttpResponseRedirect(
            root + self.model.path + 'data/%s/' % instance.pk)
