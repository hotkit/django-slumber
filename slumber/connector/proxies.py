"""
    Proxies are used as base types for instances so that new APIs can be added.
"""
from slumber.connector.ua import get


class UserProxy(object):
    """Proxy that allows forwarding of the User API.
    """

    def get_group_permissions(self):
        """Forward the group permissions.
        """
        # We're accessing attributes that are providec by the  other types
        # pylint: disable = E1101
        _, json = get(self._operations['get-permissions'])
        return set(json['group_permissions'])

