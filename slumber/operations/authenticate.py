"""
    Allows a user to be authenticated.
"""
from django.contrib.auth import authenticate

from slumber.operations import ModelOperation
from slumber.server import get_slumber_root


class AuthenticateUser(ModelOperation):
    """Allows a user to be authenticated.
    """
    def post(self, request, response, _appname, _modelname):
        """Perform the authentication.
        """
        # This method can't be a function
        # pylint: disable=R0201
        user = authenticate(**dict([(str(k), str(v))
            for k, v in request.POST.items()]))
        response['authenticated'] = bool(user)
        if user:
            root = get_slumber_root()
            response['user'] = dict(
                pk = user.pk,
                display_name = unicode(user),
                url = root + self.model.path + 'data/%s/' % user.pk)
        else:
            response['user'] = None
