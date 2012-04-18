"""
    Authentication backend that sends all of the permissions checks
    to a remote service.
"""
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from fost_authn.authentication import FostBackend

from slumber import client
from slumber.connector.proxies import attach_to_local_user


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
            "service based Slumber configuration and include a service "
            "called 'auth' which points to the service which will "
            "handle all authentication and authorization.")


class Backend(FostBackend):
    """An authentication backend which delegates user permissions to another
    Slumber service.

    Currently this backend does not support object permissions.
    """

    def authenticate(self, **kwargs):
        """Authenticate the user when the middleware passes it in.
        """
        _assert_properly_configured()
        user = super(Backend, self).authenticate(**kwargs)
        if not user:
            username = kwargs.get('username', None)
            password = kwargs.get('password', None)
            if username and password:
                user = client.auth.django.contrib.auth.User.authenticate(
                    username=username, password=password)
        return user


    # Django defines the following as methods
    # pylint: disable=R0201
    def get_user(self, user_id):
        """Return the user associated with the user_id specified.
        """
        _assert_properly_configured()
        if isinstance(user_id, int):
            local_user = User.objects.get(id=user_id)
            remote_user = \
                client.auth.django.contrib.auth.User.get(
                    **{'username':local_user.username})
        else:
            remote_user = \
                client.auth.django.contrib.auth.User.get(
                    **{'username':user_id})
        return attach_to_local_user(remote_user)

    def get_group_permissions(self, user_obj, _obj=None):
        """Returns all of the permissions the user has through their groups.
        """
        return user_obj.remote_user.get_group_permissions()

    def get_all_permissions(self, user_obj, _obj=None):
        """Return all of the permission names that this user has.
        """
        return user_obj.remote_user.get_all_permissions()

    def has_module_perms(self, user_obj, package_name):
        """Return True if the user has any permission within the
        module/application
        """
        return user_obj.remote_user.has_module_perms(package_name)

    def has_perm(self, user_obj, perm, _obj=None):
        """Return True if the user has the specified permission.
        """
        try:
            app, code = perm.split('.')
            # Pylint can't work out that objects exists on Permission
            # pylint: disable = E1101
            if Permission.objects.filter(codename=code,
                    content_type__app_label=app).count() == 0:
                content_type, _ = ContentType.objects.get_or_create(
                    app_label=app, model='unknown')
                Permission(codename=code, name=code,
                    content_type=content_type).save()
        except ValueError:
            pass
        return user_obj.remote_user.has_perm(perm)

