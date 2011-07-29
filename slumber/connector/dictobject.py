"""
    Used to allow simple initialisation of Python objects contains more or
    less any members.
"""

class DictObject(object):
    """Allows generic Python objects to be created from a nested dict
    structure describing the attrbutes.
    """
    def __init__(self, **kwargs):
        """Load the specified key values.
        """
        proc = lambda value: DictObject(**value) \
            if hasattr(value, 'items') else value
        for key, value in kwargs.items():
            if hasattr(value, 'count') and not hasattr(value, 'capitalize'):
                setattr(self, key, [proc(i) for i in value])
            else:
                setattr(self, key, proc(value))

class LazyDictObject(DictObject):
    """Allows generic Python objects to be created lazily when attributes
    are requested.
    """
    def __init__(self, getattr_function, **kwargs):
        self._getattr = getattr_function
        super(LazyDictObject, self).__init__(**kwargs)

    def __getattr__(self, name):
        return self._getattr(self, name)
