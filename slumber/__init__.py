from slumber.connector import Client

# In order to allow mocking of the Slumber client instance we need an extra
# level of indirection to give us something we can mock. The below code
# provides that.

# Create a location for where to put the real client
_client = Client()

# Create a class that just forwards to the real client
class _ClientProxy(object):
    def __getattr__(self, name):
        return getattr(_client, name)

# The client other code will import will always forward to the mockable
# _client instance.
client = _ClientProxy()
