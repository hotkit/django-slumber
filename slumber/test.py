import mock

from slumber.connector.dictobject import DictObject


def _do_get(model, **query):
    for i in model.instances:
        found = True
        for k, v in query.items():
            found = found and getattr(i, k) == v
        if found:
            return i

def mock_client(**instances):
    models = DictObject()
    for model, instances in instances.items():
        root = models
        for k in model.split('__')[:-1]:
            if not hasattr(root, k):
                setattr(root, k, DictObject())
            root = getattr(root, k)
        model_name = model.split('__')[-1]
        model_type = type(model_name, (DictObject,),{})
        setattr(model_type, 'instances', [model_type(**i) for i in instances])
        setattr(model_type, 'get', classmethod(_do_get))
        setattr(root, model_name, model_type)

    def decorator(test_method):
        @mock.patch('slumber._client', models)
        def wrapped(test):
            test_method(test)
        return wrapped
    return decorator
