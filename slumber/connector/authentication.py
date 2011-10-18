"""
    Authentication backend that sends all of the permissions checks
    to a remote service.
"""

class Backend(object):
    def authenticate(self, auto=False):
        user, created = User.objects.get_or_create(username='admin')
        print user, created
        if created:
            user.is_active = True
            user.is_staff = True
            user.save()
        return user

    def get_user(self, user_id):
        print "Getting user"
        return User.objects.get(pk=user_id)

    def get_group_permissions(self, user_obj, obj=None):
        print "get_group_permissions"
        return []

    def get_all_permissions(self, user_obj, obj=None):
        print "get_all_permissions"
        return []

    def has_module_perms(self, user_obj, package_name):
        print "has_module_perms", package_name
        return True

    def has_perm(self, user_obj, perm, obj=None):
        print "Retuning true for permission", perm
        return True
