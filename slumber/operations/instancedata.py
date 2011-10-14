"""
    Implements the server side for the instance operators.
"""
from django.core.urlresolvers import reverse

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations import InstanceOperation
from slumber.server import get_slumber_root
from slumber.server.json import to_json_data


class InstanceData(InstanceOperation):
    """Return the instance data.
    """
    def get(self, request, response, appname, modelname, pk, dataset = None):
        """Implement the fetching of attribute data for an instance.
        """
        if dataset:
            self._get_dataset(request, response, appname, modelname, pk, dataset)
        else:
            self._get_instance_data(request, response, appname, modelname, pk)

    def _get_instance_data(self, _request, response, _appname, _modelname, pk):
        """Return the base field data for the instance.
        """
        root = get_slumber_root()
        instance = self.model.model.objects.get(pk=pk)
        response['identity'] = root + self.model.path + \
            '%s/%s/' % (self.name, instance.pk)
        response['display'] = unicode(instance)
        response['operations'] = dict(
            [(op.name, root + op.path + '%s/' % instance.pk)
                for op in self.model.operations() if not op.model_operation])
        response['fields'] = {}
        for field, meta in self.model.fields.items():
            response['fields'][field] = dict(
                data=to_json_data(self.model, instance, field, meta),
                kind=meta['kind'], type=meta['type'])
        response['data_arrays'] = {}
        for field in self.model.data_arrays:
            response['data_arrays'][field] = \
                response['identity'] + '%s/' % field

    def _get_dataset(self, request, response, _appname, _modelname, pk, dataset):
        """Return one page of the array data.
        """
        root = get_slumber_root()
        instance = self.model.model.objects.get(pk=pk)
        response['instance'] = root + self.model.path + '%s/%s/%s/' % (
            self.name, str(pk), dataset)

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
