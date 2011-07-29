"""
    Implements the server side wrapper for a Django model.
"""
from django.db.models import ForeignKey
from django.db.models.fields import FieldDoesNotExist

from slumber._caches import MODEL_CACHE
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

        self._fields, self._data_arrays = {}, []

    def _get_fields_and_data_arrays(self):
        """Work out what the fields we have are.
        """
        if self._fields or self._data_arrays:
            return
        root = '/slumber/'
        # We have to access _meta
        # pylint: disable=W0212
        for field in self.model._meta.get_all_field_names():
            try:
                definition = self.model._meta.get_field(field)
                field_type = type(definition)
                if field_type == ForeignKey:
                    type_name = root + MODEL_CACHE[definition.rel.to].path
                    self._fields[field] = dict(name=field,
                        kind='object', type=type_name,
                        verbose_name=definition.verbose_name)
                else:
                    type_name = field_type.__module__ + '.' + \
                        field_type.__name__
                    self._fields[field] = dict(name=field,
                        kind='value', type=type_name,
                        verbose_name=definition.verbose_name)
            except FieldDoesNotExist:
                self._data_arrays.append(field)

    @property
    def fields(self):
        """Return the non-array fields.
        """
        self._get_fields_and_data_arrays()
        return self._fields

    @property
    def data_arrays(self):
        """Return the data array fields.
        """
        self._get_fields_and_data_arrays()
        return self._data_arrays

    def operations(self):
        """Return all of  the operations available for this model.
        """
        return [InstanceList(self, 'instances'),
                CreateInstance(self, 'create'), InstanceData(self, 'data'),
                DereferenceInstance(self, 'get')] + \
            [InstanceDataArray(self, 'data', f) for f in self.data_arrays]
