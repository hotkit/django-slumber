"""
    Proxies are used as base types for instances so that new APIs can be added.
"""


class UserProxy(object):
    """Proxy that allows forwarding of the User API.
    """

    def get_group_permissions(self):
        """Forward the group permissions.
        """
        assert False, "UserProxy.get_group_permissions Not implemented"

