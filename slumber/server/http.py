"""
    Implements the conversion of the response data to valid HTTP
    data.
"""
import logging
from simplejson import loads

from django.core.exceptions import ObjectDoesNotExist
try:
    from django.views.decorators.csrf import csrf_exempt
    USE_CSRF = True
except ImportError: # pragma: no cover
    USE_CSRF = False

from slumber.server import NotAuthorised, Forbidden, accept_handler


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


class Response(dict):
    """Subclass dict so that we can annotate it.
    """
    pass


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
            if hasattr(request, 'body'):
                request.POST = loads(request.body)
            else:
                request.POST = loads(request.raw_post_data)
        response = Response(_meta=dict(status=200, message='OK'))
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
        accepting = meta.get('HTTP_ACCEPT', 'text/plain')
        content_type, handler = accept_handler.accept(accepting)
        http_response = handler(request, response, content_type)
        for header, value in response['_meta'].get('headers', {}).items():
            http_response[header] = value
        return http_response
    return wrapper if not USE_CSRF else csrf_exempt(wrapper)

