"""
    Some basic server views.
"""
from django.http import HttpResponseRedirect, HttpResponseNotFound

from slumber.server import get_slumber_root
from slumber.server.http import view_handler
from slumber.server.meta import applications, get_application


def service_root(request):
    """Request routing for Slumber.
    """
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')
    parts = request.path[len(get_slumber_root()):-1].split('/')
    print parts
    if len(parts) == 0:
        return get_applications(request)
    elif len(parts) == 1:
        return get_modules(request, parts[0])
    elif len(parts) == 2:
        return get_model(request, parts[0], parts[1])
    return HttpResponseNotFound()


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
    response['name'] = model.name
    response['module'] = model.app.name
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

