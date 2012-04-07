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
    def post(self, request, _, appname, modelname, pk):
        """Perform the update.
        """
        @require_permission('%s.change_%s' % (appname, modelname.lower()))
        def do_update(_, request):
            """A function we can decorate which will allow us to use the
            decorator with a dynamic permission name.
            """
            instance = self.model.model.objects.get(pk=pk)
            for k, v in request.POST.items():
                setattr(instance, k, v)
            instance.save()
            return HttpResponseRedirect(
                get_slumber_root() + self.model.path + 'data/%s/'
                    % instance.pk)
        return do_update(self, request)
