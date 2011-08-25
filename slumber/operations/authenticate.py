"""
    Allows a user to be authenticated.
"""
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect

from slumber.operations import ModelOperation
from slumber.server import get_slumber_root


class AuthenticateUser(ModelOperation):
    """Allows a user to be authenticated.
    """
    def post(self, request, response, _appname, _modelname):
        """Perform the authentication.
        """
        user = authenticate(**dict([(str(k), str(v))
            for k, v in request.POST.items()]))
        if user:
            root = get_slumber_root()
            return HttpResponseRedirect(
                root + self.model.path + 'data/%s/' % user.pk)
        response['authenticated'] = False
        response['user'] = None
