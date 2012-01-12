"""
    Slumber is a RESTful client/server implementation that makes it simple
    to make use of Django models in a RESTful manner.
"""
from slumber.connector import Client
from slumber.server.configuration import configure


# In order to allow mocking of the Slumber client instance we need an extra
# level of indirection to give us something we can mock. The below code
# provides that.

# Create a location for where to put the real client
_client = Client()

class _ClientProxy(object):
    """A forwarder for the real client.
    """
    def __getattr__(self, name):
        return getattr(_client, name)

# The client other code will import will always forward to the mockable
# _client instance.
# This is exactly the name we want to use here
# pylint: disable=C0103
client = _ClientProxy()
