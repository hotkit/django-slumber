"""
    Middleware to help manage the Slumber client.
"""
import logging

from slumber._caches import PER_THREAD


# Django defines the class members as methods
# pylint: disable=R0201


class Cache(object):
    """This middleware flushes the Slumber client cache at the start
    of each request.
    """

    def process_request(self, _request):
        """Turn the cache on.
        """
        logging.info("PER_THREAD instance cache created")
        PER_THREAD.cache = type('cache', (dict,), {})()

    def process_response(self, _request, response):
        """Turn the cache off again at the end of the request and flush it.
        """
        delattr(PER_THREAD, 'cache')
        logging.info("PER_THREAD instance cache removed")
        return response


class ForwardAuthentication(object):
    """Used to forward authentication of the currently logged in user to
    another backend.
    """

    def process_request(self, request):
        """Save the request in thread local storage so it can be retrieved
        by the user agent when it makes requests.
        """
        if request.user.is_authenticated():
            PER_THREAD.username = request.user.username

    def process_response(self, _request, response):
        """Forget the request, but do an assert to make sure nothing horrible
        has happened to it first.
        """
        PER_THREAD.username = None
        return response
