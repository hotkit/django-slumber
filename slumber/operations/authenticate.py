"""
    Allows a user to be authenticated.
"""
from django.contrib.auth import authenticate

from slumber.operations import InstanceOperation


class AuthenticateUser(InstanceOperation):
    """Allows a user to be authenticated.
    """
    def post(self, request, response, _appname, _modelname, pk):
        """Perform the authentication.
        """
        instance = self.model.model.objects.get(pk=pk)
        if instance == authenticate(**request.POST):
            response['authenticated'] = True
        else:
            response['authenticated'] = False
