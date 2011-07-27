from django.db.models import ForeignKey
from django.db.models.fields import FieldDoesNotExist

from slumber.caches import MODEL_CACHE
from slumber.operations import InstanceList, CreateInstance
from slumber.operations.instancedata import DereferenceInstance, \
    InstanceData, InstanceDataArray


class DjangoModel(object):
    """Describes a Django model.
    """
    def __init__(self, app, model_instance):
        MODEL_CACHE[model_instance] = self
        self.app = app
        self.model = model_instance
        self.name = model_instance.__name__
        self.path = app.path + '/' + self.name + '/'

        self.fields, self.data_arrays = {}, []
        for field in model_instance._meta.get_all_field_names():
            try:
                definition = model_instance._meta.get_field(field)
                field_type = type(definition)
                if field_type == ForeignKey:
                    field_type = definition.rel.to
                type_name = field_type.__module__ + '.' + field_type.__name__
                self.fields[field] = dict(name=field,
                    type=type_name,
                    verbose_name=definition.verbose_name)
            except FieldDoesNotExist:
                self.data_arrays.append(field)

    def operations(self):
        """Return all of  the operations available for this model.
        """
        return [InstanceList(self, 'instances'), CreateInstance(self, 'create'),
                InstanceData(self, 'data'), DereferenceInstance(self, 'get')] + \
            [InstanceDataArray(self, 'data', f) for f in self.data_arrays]
