import mock

from slumber.connector.dictobject import DictObject


def mock_client(**instances):
    models = DictObject()
    for model, instances in instances.items():
        root = models
        for k in model.split('__'):
            if not hasattr(root, k):
                setattr(root, k, DictObject())
            root = getattr(root, k)

    def decorator(test_method):
        @mock.patch('slumber._client', models)
        def wrapped(test):
            test_method(test)
        return wrapped
    return decorator
