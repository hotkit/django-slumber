"""
    Implements configuration of the Slumber models available on the server.
"""
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL, \
    SLUMBER_MODEL_OPERATIONS
from slumber.server.json import DATA_MAPPING


def configure(django_model,
        properties_ro = None,
        to_json = None,
        operations_extra = None):
    """Configure Slumber for the provided model.

    * properties_ro : A list of properties that may be read from the client,
        but not set
    * to_json : A dict giving functions by type name which transform the
        property value to a JSON compatible Python object.
        See slumber/server/json.py for the function signatures and some
        examples
    * operations_extra: A list of operations that are to be added to the
        model.
    """
    model = DJANGO_MODEL_TO_SLUMBER_MODEL[django_model]

    model.properties['r'] += properties_ro or []
    for type_name, function in (to_json or {}).items():
        DATA_MAPPING[type_name] = function

    ops = SLUMBER_MODEL_OPERATIONS[model]
    for operation, name in operations_extra or []:
        ops.append(operation(model, name))
