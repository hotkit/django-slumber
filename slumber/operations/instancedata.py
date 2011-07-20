from django.core.urlresolvers import reverse

from datacnx.json import to_json_data
from datacnx.operations import InstanceOperation


class InstanceData(InstanceOperation):
    """Return the instance data.
    """
    def operation(self, request, response, appname, modelname, pk):
        root = reverse('slumber.views.get_applications')
        instance = self.model.model.objects.get(pk=pk)
        response['display'] = unicode(instance)
        response['fields'] = {}
        for field, meta in self.model.fields.items():
            data = getattr(instance, field)
            response['fields'][field] = dict(data=to_json_data(self.model, instance, field, meta),
                type=meta['type'])
        response['data_arrays'] = {}
        for field in self.model.data_arrays:
            response['data_arrays'][field] = root + self.model.path + '%s/%s/%s/' % (
                self.name, str(pk), field)


class InstanceDataArray(InstanceOperation):
    """Return a page from an instance's data collection.
    """
    def __init__(self, model, name, field):
        super(InstanceOperation, self).__init__(model, name)
        self.field = field
        self.regex = '([^/]+)/(%s)/' % field

    def operation(self, request, response, appname, modelname, pk, dataset):
        root = reverse('slumber.views.get_applications')
        instance = self.model.model.objects.get(pk=pk)
        response['instance'] = root + self.model.path + '%s/%s/%s/' % (
            self.name, str(pk), self.field)

        try:
            query = getattr(instance, self.field + '_set').order_by('-pk')
        except AttributeError:
            query = getattr(instance, self.field).order_by('-pk')

        response['page'] = [
                dict(pk=o.pk, display=unicode(o),
                    data=root + 'xxx/%s/' % o.pk)
            for o in query[:10]]
