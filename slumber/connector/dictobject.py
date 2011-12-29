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
        super(DictObject, self).__init__()
        proc = lambda value: DictObject(**value) \
            if hasattr(value, 'items') else value
        for key, value in kwargs.items():
            if hasattr(value, 'count') and not hasattr(value, 'capitalize'):
                setattr(self, key, [proc(i) for i in value])
            else:
                setattr(self, key, proc(value))

