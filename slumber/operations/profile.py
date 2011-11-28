"""
    Implements profile forwarding for users.
"""
from slumber.operations import InstanceOperation


class GetProfile(InstanceOperation):
    """Fetches the user proflle from the auth remote server.
    """

    def get(self, _request, response, _appname, _modelname, pk):
        """Implements the profile lookup.
        """
        user = self.model.model.objects.get(pk=pk)
