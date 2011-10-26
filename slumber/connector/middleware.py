"""
    Middleware to help manage the Slumber client.
"""
from django.contrib.auth import authenticate

from slumber import client
from slumber._caches import CLIENT_INSTANCE_CACHE


class Cache(object):
    """This middleware flushes the Slumber client cache at the start
    of each request.
    """

    # Django defines this as a method
    # pylint: disable=R0201
    def process_request(self, _request):
        """Turn the cache on.
        """
        CLIENT_INSTANCE_CACHE.enabled = True

    def process_response(self, _request, response):
        """Turn the cache off again at the end of the request and flush it.
        """
        CLIENT_INSTANCE_CACHE.enabled = False
        # We're inside Slumber so the private access is ok.
        # pylint: disable=W0212
        client._flush_client_instance_cache()
        return response


class Authentication(object):
    """Used when authentication is delegated from a remote host.
    """

    # Django defines this as a method
    # pylint: disable=R0201
    def process_request(self, request):
        """Looks for the X_FOST_User header, and if found authenticates that
        user.
        """
        user_header = request.META.get('HTTP_X_FOST_USER', None)
        if user_header:
            user = authenticate(x_fost_user=user_header)
            if user:
                request.user = user

