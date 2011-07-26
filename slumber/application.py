from slumber.model import DjangoModel


class DjangoApp(object):
    """Describes a Django application.
    """
    def __init__(self, appname):
        self.name = appname
        self.path = appname.replace('.', '/')
        self.module = __import__(appname.replace('/', '.'), globals(), locals(),
            ['models'])
        self.models = {}
        if hasattr(self.module, 'models'):
            for name in self.module.models.__dict__.keys():
                potential = getattr(self.module.models, name)
                if hasattr(potential, '_meta'):
                    dm = DjangoModel(self, potential)
                    self.models[name] = dm
