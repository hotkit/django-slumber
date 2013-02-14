"""
    Implements creation of an object.
"""
from django.core.management.color import no_style
from django.db import connection

from slumber.operations import ModelOperation
from slumber.operations.instancedata import instance_data
from slumber.server.http import require_permission
from slumber.server.json import to_json_data


class CreateInstance(ModelOperation):
    """Allows for the creation of new instances.
    """
    def post(self, request, response, appname, modelname):
        """Perform the object creation.
        """
        @require_permission('%s.add_%s' % (appname, modelname.lower()))
        def do_create(_cls, request):
            """Use an inner function so that we can generate a proper
            permission name at run time.
            """
            instance = self.model.model(**dict([(k, v)
                for k, v in request.POST.items()]))
            instance.save()
            # Reset the sequence point in case there was a PK set
            cursor = connection.cursor()
            lines = connection.ops.sequence_reset_sql(
                no_style(), [self.model.model])
            cursor.execute(';'.join(lines))
            instance_data(response, self.model, instance)
            response['pk'] = to_json_data(self.model, instance, 'pk',
                self.model.fields[self.model.model._meta.pk.name])
        return do_create(self, request)

