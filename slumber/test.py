"""
    A test version of the client.
"""
import mock

from slumber.connector.dictobject import DictObject


def _do_get(model, **query):
    """Implements a mocked version of the get operator.
    """
    for i in model.instances:
        found = True
        for k, v in query.items():
            found = found and getattr(i, k) == v
        if found:
            return i

def mock_client(**instances):
    """Replaces the client with a mocked client that provides access to the
    provided applications, models and instances.
    """
    models = DictObject()
    for model, instances in instances.items():
        root = models
        for k in model.split('__')[:-1]:
            if not hasattr(root, k):
                setattr(root, k, DictObject())
            root = getattr(root, k)
        model_name = model.split('__')[-1]
        model_type = type(model_name, (DictObject,), {})
        setattr(model_type, 'instances', [model_type(**i) for i in instances])
        setattr(model_type, 'get', classmethod(_do_get))
        setattr(root, model_name, model_type)

    def decorator(test_method):
        """The actual decorator that is going to be used on the test method.
        """
        @mock.patch('slumber._client', models)
        def wrapped(test):
            """The wrapper for the test method.
            """
            test_method(test)
        return wrapped
    return decorator
