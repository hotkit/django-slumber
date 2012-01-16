"""
    Implements profile forwarding for users.
"""
from django.core.exceptions import ObjectDoesNotExist

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.operations import InstanceOperation
from slumber.operations.instancedata import instance_data


class GetProfile(InstanceOperation):
    """Fetches the user proflle from the auth remote server.
    """

    def get(self, request, response, _appname, _modelname, pk):
        """Implements the profile lookup.
        """
        try:
            user = self.model.model.objects.get(pk=pk)
            profile = user.get_profile()
            instance_data(request, response,
                DJANGO_MODEL_TO_SLUMBER_MODEL[type(profile)],
                profile)
        except ObjectDoesNotExist:
            response['_meta']['status'] = 404
