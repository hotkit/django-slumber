"""
    Implements a listing of all instances for a given model.
"""
from dougrain import Builder

from slumber.operations import ModelOperation
from slumber.server import get_slumber_root
from slumber.server.http import require_user


class InstanceList(ModelOperation):
    """Allows access to the instances.
    """
    @require_user
    def get(self, request, response, _appname, _modelname):
        """Return a paged set of instances for this model.
        """
        root = get_slumber_root()
        response['model'] = root + self.model.path

        query = self.model.model.objects.order_by('-pk')
        if request.GET.has_key('start_after'):
            query = query.filter(pk__lt=request.GET['start_after'])

        response['page'] = [
                dict(pk=o.pk, display=unicode(o),
                    data=root + self.model.path + 'data/%s/' % o.pk)
            for o in query[:10]]
        if len(response['page']) > 0:
            response['next_page'] = root +self.model.path + \
                'instances/?start_after=%s' % response['page'][-1]['pk']


class InstanceDataHal(ModelOperation):
    """Allow us to get an instance list in HAL format.
    """
    @require_user
    def get(self, _request, response, _appname, _modelname):
        """Return a HAL formatted version of the instance list.
        """
        root = get_slumber_root()

        hal = Builder(self.uri)
        hal.add_link('model', root + self.model.path)

        query = self.model.model.objects.order_by('-pk')
        for instance in query.iterator():
            item = Builder(
                self.model.operations['data'].uri + str(instance.pk) + '/')
            item.set_property('display', unicode(instance))
            hal.embed('page', item)

        response["instances"] = hal.as_object()

