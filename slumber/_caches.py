"""
    Some caches used in the implementation of the Slumber client or server.
"""


# Stores the applications via their application names
APP_FROM_APPNAME = {}

# Stores the server model for a given Django model in the server
DJANGO_MODEL_TO_SLUMBER_MODEL = {}
# Stores the slumber models for given model URLs
MODEL_URL_TO_SLUMBER_MODEL = {}


# Stores instances in the client
CLIENT_INSTANCE_CACHE = type('cache', (dict,), {})()
# Leave the cache off by default
CLIENT_INSTANCE_CACHE.enabled = False
