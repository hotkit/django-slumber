"""
    Implements the server side wrapper for a Django model.
"""
from django.db.models import ForeignKey
from django.db.models.fields import FieldDoesNotExist

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations.authenticate import AuthenticateUser
from slumber.operations.authorization import PermissionCheck, \
    ModulePermissions, GetPermissions
from slumber.operations.create import CreateInstance
from slumber.operations.delete import DeleteInstance
from slumber.operations.instancedata import InstanceData
from slumber.operations.instancelist import InstanceList
from slumber.operations.profile import GetProfile
from slumber.operations.search import DereferenceInstance
from slumber.operations.update import UpdateInstance
from slumber.server import get_slumber_root


class NotAnOperation(Exception):
    """Thrown when an operation is looked for by name, but doesn't exist.
    """
    pass


class DjangoModel(object):
    """Describes a Django model.
    """
    def __init__(self, app, model_instance):
        DJANGO_MODEL_TO_SLUMBER_MODEL[model_instance] = self
        self.app = app
        self.model = model_instance
        self.name = model_instance.__name__
        self.path = app.path + '/' + self.name + '/'

        self.properties = dict(r=[], w=[])
        self._fields, self._data_arrays = {}, []

    def _get_fields_and_data_arrays(self):
        """Work out what the fields we have are.
        """
        if self._fields or self._data_arrays:
            return
        for field in self.model._meta.get_all_field_names():
            try:
                definition = self.model._meta.get_field(field)
                self._fields[field] = definition
            except FieldDoesNotExist:
                self._data_arrays.append(field)

    @property
    def fields(self):
        """Return the non-array fields.
        """
        self._get_fields_and_data_arrays()
        fields = {}
        for field, definition in self._fields.items():
            field_type = type(definition)
            if field_type == ForeignKey:
                fields[field] = dict(
                    name=field,
                    kind='object',
                    type= get_slumber_root() +
                        DJANGO_MODEL_TO_SLUMBER_MODEL[definition.rel.to].path,
                    verbose_name=definition.verbose_name)
            else:
                type_name = field_type.__module__ + '.' + \
                    field_type.__name__
                fields[field] = dict(name=field,
                    kind='value', type=type_name,
                    verbose_name=definition.verbose_name)
        for prop in self.properties['r']:
            fields[prop] = dict(
                name=prop,
                kind='property',
                type='.'.join([self.app.name, self.name, prop]),
                readonly=True)
        return fields

    @property
    def data_arrays(self):
        """Return the data array fields.
        """
        self._get_fields_and_data_arrays()
        return self._data_arrays

    def operations(self):
        """Return all of  the operations available for this model.
        """
        base_operations = [InstanceList(self, 'instances'),
                CreateInstance(self, 'create'),
                InstanceData(self, 'data'),
                DeleteInstance(self, 'delete'),
                DereferenceInstance(self, 'get'),
                UpdateInstance(self, 'update')]
        extra_operations = []
        if self.path == 'django/contrib/auth/User/':
            extra_operations.append(AuthenticateUser(self, 'authenticate'))
            extra_operations.append(PermissionCheck(self, 'has-permission'))
            extra_operations.append(GetPermissions(self, 'get-permissions'))
            extra_operations.append(GetProfile(self, 'get-profile'))
            extra_operations.append(ModulePermissions(
                self, 'module-permissions'))
        return base_operations + extra_operations

    def operation_by_name(self, name):
        """Return a given operation by name, or throw an exception.
        """
        ops = [o for o in self.operations() if o.name == name]
        if len(ops) != 1:
            raise NotAnOperation("Operation %s not found (options %s)" %
                (name, ops))
        else:
            return ops[0]
