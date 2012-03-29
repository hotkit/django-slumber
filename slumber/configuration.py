"""
    Implements configuration of the Slumber models available on the server.
"""
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL, \
    SLUMBER_MODEL_OPERATIONS
from slumber.connector.configuration import INSTANCE_PROXIES, MODEL_PROXIES
from slumber.server.json import DATA_MAPPING


def configure(django_model,
        properties_ro = None,
        to_json = None,
        operations_extra = None,
        instance_proxy = None,
        model_proxy = None):
    """Configure Slumber for the provided model.

    When configuring the server side the model is a model instance. When
    configuring the client the model needs to be the tail of the model path.

    Server configuration:

    * properties_ro : A list of properties that may be read from the client,
        but not set
    * to_json : A dict giving functions by type name which transform the
        property value to a JSON compatible Python object.
        See slumber/server/json.py for the function signatures and some
        examples
    * operations_extra: A list of operations that are to be added to the
        model.

    Client configuration:

    * instance_proxy: The proxy to be used on the client side when instances
    of this model are created.
    * model_proxy: The proxy to be used on the client side when this model is
        encountered.
    """
    # We need all of these arguments as they are all used
    # pylint: disable=R0913
    if django_model and isinstance(django_model, basestring):
        if instance_proxy:
            INSTANCE_PROXIES[django_model] = instance_proxy
        if model_proxy:
            MODEL_PROXIES[django_model] = model_proxy
    else:
        model = DJANGO_MODEL_TO_SLUMBER_MODEL[django_model]

        model.properties['r'] += properties_ro or []
        for type_name, function in (to_json or {}).items():
            DATA_MAPPING[type_name] = function

        ops = SLUMBER_MODEL_OPERATIONS[model]
        for operation, name in operations_extra or []:
            ops.append(operation(model, name))

