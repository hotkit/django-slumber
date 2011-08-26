"""
    Some caches used in the implementation of the Slumber client or server.
"""
import threading

# Allow some caches to be thread local
_threadlocals = threading.local()

# Stores the server model for a given Django model in the server
MODEL_CACHE = {}

# Stores instances in the client
_threadlocals.INSTANCE_CACHE = {}
