"""
    Allows a user to be authenticated.
"""
from django.contrib.auth import authenticate

from slumber.operations import ModelOperation


class AuthenticateUser(ModelOperation):
    """Allows a user to be authenticated.
    """
    def post(self, request, response, _appname, _modelname):
        """Perform the authentication.
        """
        # This method can't be a function
        # pylint: disable=R0201
        user = authenticate(**dict([(str(k), v)
            for k, v in request.POST.items()]))
        response['authenticated'] = bool(user)
        if user:
            response['user'] = dict(
                pk = user.pk,
                display_name = unicode(user),
                url = self.model.operations['data'](user))
        else:
            response['user'] = None
