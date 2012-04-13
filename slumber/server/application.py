"""
    Implements the Django application wrapper for the Slumber server.
"""
from slumber.server.model import DjangoModel


class DjangoApp(object):
    """Describes a Django application.
    """
    def __init__(self, appname):
        self.name = appname
        self.path = appname.replace('.', '/')
        self.module = __import__(appname, globals(), locals(), ['models'])
        self.models = {}
        if hasattr(self.module, 'models'):
            for name in self.module.models.__dict__.keys():
                potential = getattr(self.module.models, name)
                if hasattr(potential, '_meta') and (
                        appname == potential._meta.app_label or
                        appname.endswith('.' + potential._meta.app_label)):
                    model = DjangoModel(self, potential)
                    self.models[name] = model

    def __repr__(self):
        return self.name
