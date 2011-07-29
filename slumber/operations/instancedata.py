"""
    Implements the server side for the instance operators.
"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from slumber._caches import MODEL_CACHE
from slumber.json import to_json_data
from slumber.operations import InstanceOperation, ModelOperation


class DereferenceInstance(ModelOperation):
    """Given a primary key (or other unique set of attributes) redirects
    to the instance item."""
    def operation(self, request, _response, _appname, _modelname):
        """Work out the correct data URL for an instance we're going to
        search for.
        """
        root = reverse('slumber.views.get_applications')
        instance = self.model.model.objects.get(pk=request.GET['pk'])
        return HttpResponseRedirect(
            root + self.model.path + 'data/%s/' % instance.pk)


class InstanceData(InstanceOperation):
    """Return the instance data.
    """
    def operation(self, _request, response, _appname, _modelname, pk):
        """Implement the fetching of attribute data for an instance.
        """
        root = reverse('slumber.views.get_applications')
        instance = self.model.model.objects.get(pk=pk)
        response['display'] = unicode(instance)
        response['fields'] = {}
        for field, meta in self.model.fields.items():
            response['fields'][field] = dict(
                data=to_json_data(self.model, instance, field, meta),
                kind=meta['kind'], type=meta['type'])
        response['data_arrays'] = {}
        for field in self.model.data_arrays:
            response['data_arrays'][field] = \
                root + self.model.path + '%s/%s/%s/' % \
                    (self.name, str(pk), field)


class InstanceDataArray(InstanceOperation):
    """Return a page from an instance's data collection.
    """
    def __init__(self, model, name, field):
        super(InstanceDataArray, self).__init__(model, name)
        self.field = field
        self.regex = '([^/]+)/(%s)/' % field

    def operation(self, request, response, _appname, _modelname, pk, _dataset):
        """Return one page of the array data.
        """
        root = reverse('slumber.views.get_applications')
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
                    data=root + MODEL_CACHE[type(o)].path + 'data/%s/' % o.pk)
            for o in query[:10]]
        if len(response['page']) > 0:
            response['next_page'] = root + self.model.path + \
                '%s/%s/%s/?start_after=%s' % (
                    self.name, instance.pk, self.field,
                    response['page'][-1]['pk'])
