"""
    Implements updating of instances.
"""
from django.http import HttpResponseRedirect

from slumber.server import get_slumber_root
from slumber.operations import InstanceOperation


class UpdateInstance(InstanceOperation):
    """Update the attributes of a given instance.
    """
    def post(self, request, _response, _appname, _modelname, pk):
        """Perform the update.
        """
        instance = self.model.model.objects.get(pk=pk)
        for k, v in request.POST.items():
            setattr(instance, k, v)
        instance.save()
        return HttpResponseRedirect(
            get_slumber_root() + self.model.path + 'data/%s/' % instance.pk)
