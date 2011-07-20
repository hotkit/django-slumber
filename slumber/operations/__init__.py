from django.core.urlresolvers import reverse


class ModelOperation(object):
    """Base class for model operations.
    """
    model_operation = True
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.regex = ''
        self.path = model.path + name + '/'


class InstanceOperation(ModelOperation):
    """Base class for operations on instances.
    """
    model_operation = False
    def __init__(self, model, name):
        super(InstanceOperation, self).__init__(model, name)
        self.regex = '([^/]+)/'


class InstanceList(ModelOperation):
    """Allows access to the instances.
    """
    def operation(self, request, response, appname, modelname):
        """Return a paged set of instances for this model.
        """
        root = reverse('slumber.views.get_applications')
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


class CreateInstance(ModelOperation):
    """Allows for the creation of new instances.
    """
    def operation(self, request, response, appname, modelname):
        """Perform the object creation.
        """
        if request.method == 'POST':
            response['created'] = True
            instance = self.model.model(**dict([(k, str(v)) for k, v in request.POST.items()]))
            instance.save()
            response['pk'] = instance.pk
        else:
            response['created'] = False
