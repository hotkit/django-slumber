"""
    Implements the conversion of the response data to valid HTTP
    data.
"""
from simplejson import dumps, JSONEncoder

from django.http import HttpResponse
try:
    from django.views.decorators.csrf import csrf_exempt
    USE_CSRF = True
except ImportError: # pragma: no cover
    USE_CSRF = False

from slumber.server import NotAuthorised, Forbidden


class _proxyEncoder(JSONEncoder):
    """If we don't know how to deal with the attribute type we'll just
    convert to a string and hope that's ok for now.
    """
    # An attribute inherited from JSONEncoder hide this method
    # pylint: disable=E0202
    def default(self, obj):
        return unicode(obj)


def require_user(function):
    """Throw NotAuthorised if the view is accessed anonymously.
    """
    def decorated(cls, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise NotAuthorised()
        return function(cls, request, *args, **kwargs)
    return decorated


def require_permission(permission):
    """Throw Forbidden if the user does not have the required permission
    """
    def decorator(function):
        @require_user
        def decorated(request, *args, **kwargs):
            return function(request, *args, **kwargs)
    return decorator


def view_handler(view):
    """Wrap a view function so it can return either JSON, HTML or some
    other response.
    """
    def wrapper(request, *args, **kwargs):
        """The decorated implementation.
        """
        response = {'_meta': dict(status=200, message='OK')}
        try:
            http_response = view(request, response, *args, **kwargs)
            if http_response:
                return http_response
        except NotAuthorised, _:
            response = {'_meta': dict(status=401, message='Unauthorized'),
                'error': 'No user is logged in'}
        except Forbidden, e:
            response = {'_meta': dict(status=403, message='Forbidden'),
                'error': unicode(e)}
        except NotImplementedError, _:
            response = {
                '_meta': dict(status=501, message='Not Implemented'),
                'error': "Not implemented"}
        return HttpResponse(dumps(response, indent=4,
                cls=_proxyEncoder), 'text/plain',
            status=response['_meta']['status'])
    return wrapper if not USE_CSRF else csrf_exempt(wrapper)

