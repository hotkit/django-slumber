"""
    Implements the server side for the instance operators.
"""
from django.core.urlresolvers import reverse

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations import InstanceOperation
from slumber.server.json import to_json_data


class InstanceData(InstanceOperation):
    """Return the instance data.
    """
    def get(self, _request, response, _appname, _modelname, pk):
        """Implement the fetching of attribute data for an instance.
        """
        root = reverse('slumber.server.views.get_applications')
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


class InstanceDataArray(InstanceOperation):
    """Return a page from an instance's data collection.
    """
    def __init__(self, model, name, field):
        super(InstanceDataArray, self).__init__(model, name)
        self.field = field
        self.regex = '([^/]+)/(%s)/' % field

    def get(self, request, response, _appname, _modelname, pk, _dataset):
        """Return one page of the array data.
        """
        root = reverse('slumber.server.views.get_applications')
        instance = self.model.model.objects.get(pk=pk)
        response['instance'] = root + self.model.path + '%s/%s/%s/' % (
            self.name, str(pk), self.field)

        try:
            query = getattr(instance, self.field + '_set')
        except AttributeError:
            query = getattr(instance, self.field)
        query = query.order_by('-pk')
        if request.GET.has_key('start_after'):
            query = query.filter(pk__lt=request.GET['start_after'])

        response['page'] = [
                dict(pk=o.pk, display=unicode(o),
                    data=root + DJANGO_MODEL_TO_SLUMBER_MODEL[type(o)].path +
                        'data/%s/' % o.pk)
            for o in query[:10]]
        if len(response['page']) > 0:
            response['next_page'] = root + self.model.path + \
                '%s/%s/%s/?start_after=%s' % (
                    self.name, instance.pk, self.field,
                    response['page'][-1]['pk'])
