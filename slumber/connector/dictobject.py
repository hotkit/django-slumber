

class DictObject(object):
    """Allows generic Python objects to be created from a nested dict
    structure describing the attrbutes.
    """
    def __init__(self, **kwargs):
        """Load the specified key values.
        """
        proc = lambda v: DictObject(**v) if hasattr(v, 'items') else v
        for k, v in kwargs.items():
            if hasattr(v, 'count') and not hasattr(v, 'capitalize'):
                setattr(self, k, [proc(i) for i in v])
            else:
                setattr(self, k, proc(v))

class LazyDictObject(DictObject):
    """Allows generic Python objects to be created lazily when attributes are requested.
    """
    def __init__(self, getattr_function, **kwargs):
        self._getattr = getattr_function
        super(LazyDictObject, self).__init__(**kwargs)

    def __getattr__(self, name):
        return self._getattr(self, name)
