"""
    Some basic server views.
"""
from django.http import HttpResponseRedirect, HttpResponseNotFound

from slumber.server.http import view_handler
from slumber.server.meta import applications, get_application
from slumber.server.configuration import get_slumber_root

@view_handler
def get_applications(request, response):
    """Return the list of applications and the dataconnection URLs for them.
    """
    root = get_slumber_root()
    if request.GET.has_key('model'):
        appname, modelname = request.GET['model'].split('.')
        for app in applications():
            if app.name.endswith(appname) and app.models.has_key(modelname):
                return HttpResponseRedirect(root + app.models[modelname].path)
        return HttpResponseNotFound()
    response['apps'] = dict([(app.name, root + app.path + '/')
        for app in applications()])


@view_handler
def get_models(_, response, appname):
    """Return the models that comprise an application.
    """
    root = get_slumber_root()
    app = get_application(appname)
    response['models'] = dict([(n, root + m.path)
        for n, m in app.models.items()])


@view_handler
def get_model(_, response, appname, modelname):
    """Return meta data about the model.
    """
    app = get_application(appname)
    model = app.models[modelname]
    response['fields'] = model.fields
    # We have to access _meta
    # pylint: disable=W0212
    response['puttable'] = [[f] for f in model.fields
        if model.model._meta.get_field(f).unique] + \
        list(model.model._meta.unique_together)
    response['data_arrays'] = model.data_arrays
    response['operations'] = dict(
        [(op.name, get_slumber_root() + op.path)
            for op in model.operations() if op.model_operation])

