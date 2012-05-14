"""
    Implements the conversion of the response data to valid HTTP
    data.
"""
import logging
from simplejson import dumps, JSONEncoder, loads

from django.core.exceptions import ObjectDoesNotExist
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
        """The docorated function.
        """
        logging.debug("User %s is_authenticated: %s", request.user,
            request.user.is_authenticated())
        if not request.user.is_authenticated():
            raise NotAuthorised()
        return function(cls, request, *args, **kwargs)
    return decorated


def require_permission(permission):
    """Throw Forbidden if the user does not have the required permission
    """
    def decorator(function):
        """The decorator returned from its configuration function.
        """
        @require_user
        def decorated(cls, request, *args, **kwargs):
            """The decorated view function.
            """
            if not request.user.has_perm(permission):
                raise Forbidden("Requires permission %s" % permission)
            return function(cls, request, *args, **kwargs)
        return decorated
    return decorator


def view_handler(view):
    """Wrap a view function so it can return either JSON, HTML or some
    other response.
    """
    def wrapper(request, *args, **kwargs):
        """The decorated implementation.
        """
        meta = request.META
        if meta.get('CONTENT_TYPE', '').startswith('application/json') and \
                meta.get('CONTENT_LENGTH'):
            request.POST = loads(request.raw_post_data)
        response = {'_meta': dict(status=200, message='OK')}
        try:
            http_response = view(request, response, *args, **kwargs)
            if http_response:
                return http_response
        except NotAuthorised, _:
            response = {
                '_meta': dict(status=401, message='Unauthorized',
                    headers= {'WWW-Authenticate':'FOST Realm="Slumber"'}),
                'error': 'No user is logged in'}
        except Forbidden, exception:
            response = {'_meta': dict(status=403, message='Forbidden'),
                'error': unicode(exception)}
        except ObjectDoesNotExist, exception:
            response = {'_meta': dict(status=404, message='Not Found'),
                'error': unicode(exception)}
        except NotImplementedError, _:
            response = {
                '_meta': dict(status=501, message='Not Implemented'),
                'error': "Not implemented"}
        if request.user.is_authenticated():
            response['_meta']['username'] = request.user.username
        else:
            logging.debug("Request user %s not authenticated", request.user)
        http_response = HttpResponse(dumps(response, indent=4,
                cls=_proxyEncoder), 'text/plain',
            status=response['_meta']['status'])
        for header, value in response['_meta'].get('headers', {}).items():
            http_response[header] = value
        return http_response
    return wrapper if not USE_CSRF else csrf_exempt(wrapper)

