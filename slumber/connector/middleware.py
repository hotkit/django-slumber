"""
    Middleware to help manage the Slumber client.
"""
from slumber import client


class Cache(object):
    """This middleware flushes the Slumber client cache at the start
    of each request.
    """

    # Django defines this as a method
    # pylint: disable=R0201
    def process_request(self, _request):
        """Flush the queue before any other processing is done.
        """
        # We're inside Slumber so the private access is ok.
        # pylint: disable=W0212
        client._flush_client_instance_cache()
