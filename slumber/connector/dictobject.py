

class DictObject(object):
    """Allows generic Python objects to be created from a nested dict
    structure describing the attrbutes.
    """
    def __init__(self, **kwargs):
        """Load the specified key values.
        """
        for k, v in kwargs.items():
            if hasattr(v, 'items'):
                setattr(self, k, DictObject(**v))
            else:
                setattr(self, k, v)

class LazyDictObject(DictObject):
    """Allows generic Python objects to be created lazily when attributes are requested.
    """
    def __init__(self, getattr_function, **kwargs):
        self._getattr = getattr_function
        super(LazyDictObject, self).__init__(**kwargs)

    def __getattr__(self, name):
        return self._getattr(self, name)
