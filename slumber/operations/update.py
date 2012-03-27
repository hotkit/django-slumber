"""
    Implements updating of instances.
"""
from django.http import HttpResponseRedirect

from slumber.operations import InstanceOperation
from slumber.server import get_slumber_root
from slumber.server.http import require_permission


class UpdateInstance(InstanceOperation):
    """Update the attributes of a given instance.
    """
    @require_permission('appname.update_model')
    def post(self, request, _response, _appname, _modelname, pk):
        """Perform the update.
        """
        instance = self.model.model.objects.get(pk=pk)
        for k, v in request.POST.items():
            setattr(instance, k, v)
        instance.save()
        return HttpResponseRedirect(
            get_slumber_root() + self.model.path + 'data/%s/' % instance.pk)
