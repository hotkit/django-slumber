"""
    Middleware to help manage the Slumber client.
"""
from slumber import client
from slumber._caches import CLIENT_INSTANCE_CACHE, PER_THREAD


# Django defines the class members as methods
# pylint: disable=R0201


class Cache(object):
    """This middleware flushes the Slumber client cache at the start
    of each request.
    """

    def process_request(self, _request):
        """Turn the cache on.
        """
        CLIENT_INSTANCE_CACHE.enabled = True

    def process_response(self, _request, response):
        """Turn the cache off again at the end of the request and flush it.
        """
        CLIENT_INSTANCE_CACHE.enabled = False
        client._flush_client_instance_cache()
        return response


class ForwardAuthentication(object):
    """Used to forward authentication of the currently logged in user to
    another backend.
    """

    def process_request(self, request):
        """Save the request in thread local storage so it can be retrieved
        by the user agent when it makes requests.
        """
        PER_THREAD.request = request

    def process_response(self, request, response):
        """Forget the request, but do an assert to make sure nothing horrible
        has happened to it first.
        """
        assert PER_THREAD.request is request
        PER_THREAD.request = None
        PER_THREAD.username = None
        return response
