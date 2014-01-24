"""
    Implements the server side wrapper for a Django model.
"""
from django.db.models import ForeignKey, ManyToManyField
from django.db.models.fields import FieldDoesNotExist

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations.authenticate import AuthenticateUser
from slumber.operations.authorization import CheckMyPermission, \
    PermissionCheck, ModulePermissions, GetPermissions
from slumber.operations.create import CreateInstance
from slumber.operations.delete import DeleteInstance
from slumber.operations.instancedata import InstanceData
from slumber.operations.instancelist import InstanceList
from slumber.operations.profile import GetProfile
from slumber.operations.search import DereferenceInstance
from slumber.operations.update import UpdateInstance
from slumber.server import get_slumber_root


class DjangoModel(object):
    """Describes a Django model.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, app, model_instance):
        DJANGO_MODEL_TO_SLUMBER_MODEL[model_instance] = self
        self.app = app
        self.model = model_instance
        self.model.slumber_model = self
        self.name = model_instance.__name__
        self.path = app.path + '/' + self.name + '/'

        self.properties = dict(r=[], w=[])
        self._fields, self._data_arrays = {}, []
        self.operations = {
            'instances': InstanceList(self, 'instances'),
            'create': CreateInstance(self, 'create'),
            'data': InstanceData(self, 'data'),
            'delete': DeleteInstance(self, 'delete'),
            'get': DereferenceInstance(self, 'get'),
            'update': UpdateInstance(self, 'update')
        }
        if self.path == 'django/contrib/auth/User/':
            self.operations['do-i-have-perm'] = \
                CheckMyPermission(self, 'do-i-have-perm')
            self.operations['authenticate'] = \
                AuthenticateUser(self, 'authenticate')
            self.operations['has-permission'] = \
                PermissionCheck(self, 'has-permission')
            self.operations['get-permissions'] = \
                GetPermissions(self, 'get-permissions')
            self.operations['get-profile'] = \
                GetProfile(self, 'get-profile')
            self.operations['module-permissions'] = \
                ModulePermissions(self, 'module-permissions')

    def __repr__(self):
        return "%s.%s" % (self.app, self.name)

    def _get_fields_and_data_arrays(self):
        """Work out what the fields we have are.
        """
        if self._fields or self._data_arrays:
            return
        for field in self.model._meta.get_all_field_names():
            try:
                definition = self.model._meta.get_field(field)
                if type(definition) == ManyToManyField:
                    self._data_arrays.append(field)
                else:
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
