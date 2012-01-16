"""
    Implements the server side for the instance operators.
"""
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations import InstanceOperation
from slumber.server import get_slumber_root
from slumber.server.json import to_json_data


def instance_data(request, into, model, instance):
    """Fill in the dict `into` with information about the instance of the
    specified model.
    """
    root = get_slumber_root()
    into['type'] = root + model.path
    into['identity'] = root + model.path + \
        '%s/%s/' % ('data', instance.pk)
    into['display'] = unicode(instance)
    into['operations'] = dict(
        [(op.name, root + op.path + '%s/' % instance.pk)
            for op in model.operations() if not op.model_operation])
    into['fields'] = {}
    for field, meta in model.fields.items():
        into['fields'][field] = dict(
            data=to_json_data(request, model, instance, field, meta),
            kind=meta['kind'], type=meta['type'])
    into['data_arrays'] = {}
    for field in model.data_arrays:
        into['data_arrays'][field] = \
            into['identity'] + '%s/' % field


class InstanceData(InstanceOperation):
    """Return the instance data.
    """
    def get(self, request, response, _appname, _modelname, pk, dataset = None):
        """Implement the fetching of attribute data for an instance.
        """
        instance = self.model.model.objects.get(pk=pk)
        if dataset:
            self._get_dataset(request, response, instance, dataset)
        else:
            self._get_instance_data(request, response, instance)

    def _get_instance_data(self, request, response, instance):
        """Return the base field data for the instance.
        """
        return instance_data(request, response, self.model, instance)

    def _get_dataset(self, request, response, instance, dataset):
        """Return one page of the array data.
        """
        root = get_slumber_root()
        response['instance'] = root + self.model.path + '%s/%s/%s/' % (
            self.name, str(instance.pk), dataset)

        try:
            query = getattr(instance, dataset + '_set')
        except AttributeError:
            query = getattr(instance, dataset)
        query = query.order_by('-pk')
        if request.GET.has_key('start_after'):
            query = query.filter(pk__lt=request.GET['start_after'])

        response['page'] = []
        for obj in query[:10]:
            model = DJANGO_MODEL_TO_SLUMBER_MODEL[type(obj)]
            response['page'].append(dict(
                    type=root + model.path,
                    pk=obj.pk, display=unicode(obj),
                    data=root + model.path + 'data/%s/' % obj.pk))

        if query.count() > len(response['page']):
            response['next_page'] = root + self.model.path + \
                '%s/%s/%s/?start_after=%s' % (
                    self.name, instance.pk, dataset,
                    response['page'][-1]['pk'])
