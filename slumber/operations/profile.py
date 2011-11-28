"""
    Implements profile forwarding for users.
"""
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations import InstanceOperation
from slumber.operations.instancedata import instance_data


class GetProfile(InstanceOperation):
    """Fetches the user proflle from the auth remote server.
    """

    def get(self, _request, response, _appname, _modelname, pk):
        """Implements the profile lookup.
        """
        user = self.model.model.objects.get(pk=pk)
        profile = user.get_profile()
        instance_data(response,
            DJANGO_MODEL_TO_SLUMBER_MODEL[type(profile)],
            profile)

