"""
    Authentication backend that sends all of the permissions checks
    to a remote service.
"""
from django.contrib.auth.models import User

from slumber import client


class ImproperlyConfigured(Exception):
    """Raised if the authentication is not configured as it should be.
    """
    pass


def _assert_properly_configured():
    """Make sure that the authentication backend is properly configured.
    """
    if not hasattr(client, 'auth'):
        raise ImproperlyConfigured("If using the Slumber client's "
            "authentication backend then you must also use the full "
            "service based Slumber confiuration and include a service "
            "called 'auth' which points to the service which will "
            "handle all authentication and authorization.")


class Backend(object):
    """An authentication backend which delegates user permissions to another
    Slumber service.
    """

    # Django defines this as a method
    # pylint: disable=R0201
    def authenticate(self, username=None):
        """Authenticate the user when the middleware passes it in.
        """
        return self.get_user(username)

    def get_user(self, user_id):
        """Return the user associated with the user_id specified.
        """
        _assert_properly_configured()
        try:
            remote_user = client.auth.django.contrib.auth.User.get(
                username=user_id)
        except AssertionError:
            return None
        user, created = User.objects.get_or_create(username=user_id)
        if created:
            for attr in ['is_active', 'is_staff']:
                setattr(user, attr, getattr(remote_user, attr))
            user.save()
        user.remote_user = remote_user
        return user

    def get_group_permissions(self, user_obj, _obj=None):
        """Returns all of the permissions the user has through their groups.
        """
        return user_obj.remote_user.get_group_permissions()

    #def get_all_permissions(self, user_obj, obj=None):
        #print "get_all_permissions"
        #return []

    #def has_module_perms(self, user_obj, package_name):
        #print "has_module_perms", package_name
        #return True

    #def has_perm(self, user_obj, perm, obj=None):
        #print "Retuning true for permission", perm
        #return True
