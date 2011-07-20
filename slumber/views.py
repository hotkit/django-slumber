from simplejson import dumps

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse

from slumber.http import view_handler
from slumber.meta import applications, get_application


@view_handler
def get_applications(request, response):
    """Return the list of applications and the dataconnection URLs for them.
    """
    root = reverse('slumber.views.get_applications')
    if request.GET.has_key('model'):
        appname, modelname = request.GET['model'].split('.')
        for app in applications():
            if app.name.endswith(appname) and app.models.has_key(modelname):
                return HttpResponseRedirect(root + app.models[modelname].path)
        return HttpResponseNotFound()
    response['apps'] = dict([(app.name, root + app.path + '/')
        for app in applications()])


@view_handler
def get_models(request, response, appname):
    """Return the models that comprise an application.
    """
    root = reverse('slumber.views.get_applications')
    app = get_application(appname)
    response['models'] = dict([(n, root + m.path)
        for n, m in app.models.items()])


@view_handler
def get_model(request, response, appname, modelname):
    """Return meta data about the model.
    """
    app = get_application(appname)
    model = app.models[modelname]
    response['fields'] = model.fields
    # TODO If the id field is a django.db.models.fields.AutoField then we
    # should not include it in the puttable fields
    response['puttable'] = [[f] for f in model.fields if model.model._meta.get_field(f).unique] + \
        list(model.model._meta.unique_together)
    response['data_arrays'] = model.data_arrays
    response['operations'] = dict(
        [(op.name, reverse('slumber.views.get_applications') + op.path)
            for op in model.operations() if op.model_operation])

