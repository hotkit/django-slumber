"""
    Implements the server side for the instance operators.
"""
from slumber.operations import InstanceOperation
from slumber.server import get_slumber_root
from slumber.server.http import require_user
from slumber.server.json import to_json_data


def instance_data(into, model, instance):
    """Fill in the dict `into` with information about the instance of the
    specified model.
    """
    root = get_slumber_root()
    into['type'] = root + model.path
    into['identity'] = root + model.path + \
        '%s/%s/' % ('data', instance.pk)
    into['display'] = unicode(instance)
    into['operations'] = dict(
        [(op.name, op(instance))
            for op in model.operations.values() if not op.model_operation])
    into['fields'] = {}
    for field, meta in model.fields.items():
        into['fields'][field] = dict(
            data=to_json_data(model, instance, field, meta),
            kind=meta['kind'], type=meta['type'])
    into['data_arrays'] = {}
    for field in model.data_arrays:
        into['data_arrays'][field] = \
            into['identity'] + '%s/' % field


class InstanceData(InstanceOperation):
    """Return the instance data.
    """
    @require_user
    def get(self, request, response, _appname, _modelname, pk, dataset = None):
        """Implement the fetching of attribute data for an instance.
        """
        instance = self.model.model.objects.get(pk=pk)
        if dataset:
            self._get_dataset(request, response, instance, dataset)
        else:
            self._get_instance_data(request, response, instance)

    def _get_instance_data(self, _request, response, instance):
        """Return the base field data for the instance.
        """
        return instance_data(response, self.model, instance)

    def _get_dataset(self, request, response, instance, dataset):
        """Return one page of the array data.
        """
        root = get_slumber_root()
        response['instance'] = self(instance, dataset)

        try:
            query = getattr(instance, dataset + '_set')
        except AttributeError:
            query = getattr(instance, dataset)
        query = query.order_by('-pk')
        if request.GET.has_key('start_after'):
            query = query.filter(pk__lt=request.GET['start_after'])

        response['page'] = []
        for obj in query[:10]:
            model = type(obj).slumber_model
            response['page'].append(dict(
                    type=root + model.path,
                    pk=obj.pk, display=unicode(obj),
                    data=model.operations['data'](obj)))

        if query.count() > len(response['page']):
            response['next_page'] = self(instance, dataset,
                start_after=response['page'][-1]['pk'])

