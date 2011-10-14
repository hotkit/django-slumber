"""
    Some basic server views.
"""
from django.http import HttpResponseRedirect, HttpResponseNotFound

from slumber.server import get_slumber_root
from slumber.server.http import view_handler
from slumber.server.meta import applications, get_application


@view_handler
def service_root(request, response):
    """Request routing for Slumber.
    """
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')
    path = request.path[len(get_slumber_root()):-1]
    if not path:
        return get_applications(request, response)
    else:
        # Find the app with the longest matching path
        print path
        apps = [a for a in applications() if path.startswith(a.path)]
        print apps
        app = None
        for a in apps:
            if not app or len(a.path) > len(app.path):
                app = a
        remaining_path = path[len(app.path)+1:]
        if not remaining_path:
            return get_models(request, response, app.path)

        models = remaining_path.split('/')
        print app, models
        # Find the model instance and possibly return its details
        model = app.models.get(models.pop(0), None)
        if not model:
            return HttpResponseNotFound()
        if len(models) == 0:
            return get_model(request, response, app.path, model.name)

        operation = model.operation_by_name(models.pop(0))
        return operation.operation(request, response,
            app.path, model.name, *models)


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


def get_models(_, response, appname):
    """Return the models that comprise an application.
    """
    root = get_slumber_root()
    app = get_application(appname)
    response['models'] = dict([(n, root + m.path)
        for n, m in app.models.items()])


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

