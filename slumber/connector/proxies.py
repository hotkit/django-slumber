"""
    Proxies are used as base types for instances so that new APIs can be added.
"""
from urlparse import urljoin

from django.contrib.auth.models import User

from slumber.connector.api import get_instance_from_data
from slumber.connector.configuration import INSTANCE_PROXIES, MODEL_PROXIES
from slumber.connector.ua import get, post


def attach_to_local_user(remote_user):
    """Return the local user with the remote user object attached to it.
    """
    user, _ = User.objects.get_or_create(username=remote_user.username)
    for attr in ['is_active', 'is_staff', 'date_joined', 'is_superuser',
            'first_name', 'last_name', 'email']:
        v = getattr(remote_user, attr)
        setattr(user, attr, v)
    user.save()
    user.remote_user = remote_user
    # This lambda is necessary, but no idea why
    # pylint: disable = W0108
    user.get_profile = lambda: remote_user.get_profile()
    return user


class UserInstanceProxy(object):
    """Proxy that allows forwarding of the User API.
    """
    def __init__(self, *a, **kw):
        super(UserInstanceProxy, self).__init__(*a, **kw)
        self._CACHE_TTL = 120

    def has_perm(self, permission):
        """Forward the permission check.
        """
        # We're accessing attributes that are provided by the  other types
        # pylint: disable = E1101
        _, json = get(
            urljoin(self._operations['has-permission'], permission),
            self._CACHE_TTL)
        return json['is-allowed']

    def has_module_perms(self, module):
        """Forward the permission check.
        """
        # We're accessing attributes that are provided by the  other types
        # pylint: disable = E1101
        _, json = get(
            urljoin(self._operations['module-permissions'], module),
            self._CACHE_TTL)
        return json['has_module_perms']

    def get_group_permissions(self):
        """Forward the group permissions.
        """
        # We're accessing attributes that are provided by the  other types
        # pylint: disable = E1101
        _, json = get(self._operations['get-permissions'], self._CACHE_TTL)
        return set(json['group_permissions'])

    def get_all_permissions(self):
        """Forward access to all of the permissions.
        """
        # We're accessing attributes that are provided by the  other types
        # pylint: disable = E1101
        _, json = get(self._operations['get-permissions'], self._CACHE_TTL)
        return set(json['all_permissions'])

    def get_profile(self):
        """Forward access to the profile.
        """
        # We're accessing attributes that are provided by the  other types
        # pylint: disable = E1101
        base_url = self._operations['get-profile']
        _, json = get(base_url, self._CACHE_TTL)
        return get_instance_from_data(base_url, json)

INSTANCE_PROXIES['django/contrib/auth/User/'] = UserInstanceProxy


class UserModelProxy(object):
    """Contains the model methods that need to be exposed within the client.
    """
    def __init__(self, *a, **kw):
        super(UserModelProxy, self).__init__(*a, **kw)
        self._CACHE_TTL = 120

    def authenticate(self, **kwargs):
        """Allow a forwarded request for authentication.
        """
        # We're accessing attributes that are providec by the  other types
        # pylint: disable = E1101
        _, json = post(self._operations['authenticate'], kwargs)
        if json['authenticated']:
            # Pylint can't see the __call__ implemented in another base class
            # pylint: disable = E1102
            remote_user = self(urljoin(self._url, json['user']['url']),
                json['user']['display_name'])
            return attach_to_local_user(remote_user)

MODEL_PROXIES['django/contrib/auth/User/'] = UserModelProxy

