"""
    Implements configuration of the Slumber models available on the server.
"""
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL


def configure(django_model,
        properties_ro = None):
    """Configure Slumber for the provided model.

    * properties_ro : A list of properties that may be read from the client,
        but not set
    """
    model = DJANGO_MODEL_TO_SLUMBER_MODEL[django_model]

    model.properties['r'].append(properties_ro or [])
