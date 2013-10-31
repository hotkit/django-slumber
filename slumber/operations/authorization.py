"""
    Implements authorization checks for users.
"""
from slumber.operations import InstanceOperation, ModelOperation


class CheckMyPermission(ModelOperation):
    """Allows for checking if the current user has a specific permission.
    """

    def get(self, request, response, _appname, _modelname, permission=None):
        """Implements the permission lookup.
        """
        # pylint: disable=R0201
        response['permissions'] = {}
        permissions = []
        if permission:
            permissions.append(permission)
        for perm in request.GET.getlist('q'):
            permissions.append(perm)
        for perm in permissions:
            response['permissions'][perm] = request.user.has_perm(perm)


class PermissionCheck(InstanceOperation):
    """Allows for checking if a given user has a specific permission.
    """

    def get(self, _request, response, _appname, _modelname, pk, permission):
        """Implements the permission lookup.
        """
        user = self.model.model.objects.get(pk=pk)
        response['is-allowed'] = user.has_perm(permission)


class ModulePermissions(InstanceOperation):
    """Allows us to check if the user has any permissions for the module.
    """

    def get(self, _request, response, _appname, _modelname, pk, module):
        """Implements the wrapper.
        """
        user = self.model.model.objects.get(pk=pk)
        response['has_module_perms'] = user.has_module_perms(module)


class GetPermissions(InstanceOperation):
    """Exposes the get_group_permissions API on Users.
    """

    def get(self, _request , response, _appname, _modelname, pk):
        """Implements the API.
        """
        user = self.model.model.objects.get(pk=pk)
        response['group_permissions'] = list(user.get_group_permissions())
        response['all_permissions'] = list(user.get_all_permissions())

