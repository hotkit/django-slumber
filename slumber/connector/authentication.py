"""
    Authentication backend that sends all of the permissions checks
    to a remote service.
"""
from django.contrib.auth.models import User

from slumber import client


class Backend(object):
    """An authentication backend which delegates user permissions to another
    Slumber service.
    """

    # Django defines this as a method
    # pylint: disable=R0201
    def authenticate(self, username=None):
        """Authenticate the user when the middleware passes it in.
        """
        user, created = User.objects.get_or_create(username=username)
        if created:
            try:
                remote_user = client.django.contrib.auth.User.get(
                    username=username)
                for attr in ['is_active', 'is_staff']:
                    setattr(user, attr, getattr(remote_user, attr))
                user.save()
            except AssertionError:
                return None
        return user

    #def get_user(self, user_id):
        #print "Getting user"
        #return User.objects.get(pk=user_id)

    #def get_group_permissions(self, user_obj, obj=None):
        #print "get_group_permissions"
        #return []

    #def get_all_permissions(self, user_obj, obj=None):
        #print "get_all_permissions"
        #return []

    #def has_module_perms(self, user_obj, package_name):
        #print "has_module_perms", package_name
        #return True

    #def has_perm(self, user_obj, perm, obj=None):
        #print "Retuning true for permission", perm
        #return True
