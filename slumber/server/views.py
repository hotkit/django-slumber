"""
    Some basic server views.
"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, \
    HttpResponsePermanentRedirect, HttpResponseNotFound

from slumber.server import get_slumber_service, get_slumber_root, \
    get_slumber_services
from slumber.server.http import view_handler
from slumber.server.meta import applications
from slumber.server.model import NotAnOperation


@view_handler
def service_root(request, response):
    """Request routing for Slumber.
    """
    # We have many return statements, but there's no point in artificially
    # breaking the function up to reduce them
    # pylint: disable = R0911
    if not request.path.endswith('/'):
        return HttpResponsePermanentRedirect(request.path + '/')
    path = request.path[len(reverse('slumber.server.views.service_root')):-1]
    service = get_slumber_service()
    if service:
        if not path:
            return get_service_directory(request, response, service)
        elif not path.startswith(service + '/') and path != service:
            return HttpResponseNotFound()
        path = path[len(service) + 1:]

    if not path:
        return get_applications(request, response)
    else:
        # Find the app with the longest matching path
        apps = [a for a in applications() if path.startswith(a.path)]
        application = None
        for app in apps:
            if not application or len(app.path) > len(application.path):
                application = app
        remaining_path = path[len(application.path)+1:]
        if not remaining_path:
            return get_models(request, response, application)

        models = remaining_path.split('/')
        # Find the model instance and possibly return its details
        model = application.models.get(models.pop(0), None)
        if len(models) == 0:
            return get_model(request, response, model)

        try:
            # Execute the operation (if it can be found)
            operation_name = models.pop(0)
            operation = model.operation_by_name(operation_name)
            return operation.operation(request, response,
                application.path, model.name, *models)
        except NotAnOperation:
            return HttpResponseNotFound()


def get_service_directory(_request, response, service):
    """Return the services.
    """
    directory = get_slumber_services()
    if directory or not service:
        response['services'] = directory
    else:
        response['services'] = {}
        response['services'][service] = get_slumber_root()


def get_applications(request, response):
    """Return the list of applications and the data connection URLs for them.
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
    get_service_directory(request, response, None)


def get_models(_, response, app):
    """Return the models that comprise an application.
    """
    root = get_slumber_root()
    response['models'] = dict([(n, root + m.path)
        for n, m in app.models.items()])


def get_model(_, response, model):
    """Return meta data about the model.
    """
    if not model:
        return HttpResponseNotFound()
    root = get_slumber_root()
    response['name'] = model.name
    response['module'] = model.app.name
    response['fields'] = model.fields
    response['puttable'] = [[f] for f, p in model.fields.items()
            if p['kind'] != 'property' and
                model.model._meta.get_field(f).unique] + \
        list(model.model._meta.unique_together)
    response['data_arrays'] = model.data_arrays
    response['operations'] = dict(
        [(op.name, root + op.path)
            for op in model.operations() if op.model_operation])

