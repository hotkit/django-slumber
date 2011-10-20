"""
    Proxies are used as base types for instances so that new APIs can be added.
"""
from urlparse import urljoin

from slumber.connector.ua import get


class UserProxy(object):
    """Proxy that allows forwarding of the User API.
    """

    def has_perm(self, permission):
        """Forward the permission check.
        """
        # We're accessing attributes that are providec by the  other types
        # pylint: disable = E1101
        _, json = get(urljoin(self._operations['has-permission'], permission))
        return json['is-allowed']

    def has_module_perms(self, module):
        """Forward the permission check.
        """
        # We're accessing attributes that are providec by the  other types
        # pylint: disable = E1101
        _, json = get(urljoin(self._operations['module-permissions'], module))
        return json['has_module_perms']

    def get_group_permissions(self):
        """Forward the group permissions.
        """
        # We're accessing attributes that are providec by the  other types
        # pylint: disable = E1101
        _, json = get(self._operations['get-permissions'])
        return set(json['group_permissions'])

    def get_all_permissions(self):
        """Forward access to all of the permissions.
        """
        # We're accessing attributes that are providec by the  other types
        # pylint: disable = E1101
        _, json = get(self._operations['get-permissions'])
        return set(json['all_permissions'])
