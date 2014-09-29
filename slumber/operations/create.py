"""
    Implements creation of an object.
"""
from slumber.operations import ModelOperation
from slumber.operations.instancedata import \
    instance_data, _reset_sequence_number
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
            key_name = self.model.model._meta.pk.name
            if not request.POST.has_key(key_name):
                created = True
            else:
                filter_args = {key_name: request.POST[key_name]}
                objects = self.model.model.objects
                created = (objects.filter(**filter_args).count() == 0)

            instance = self.model.model(**dict([(k, v)
                for k, v in request.POST.items()]))
            instance.save()
            _reset_sequence_number(self.model.model)

            instance_data(response, self.model, instance)
            response['pk'] = to_json_data(self.model, instance, key_name,
                self.model.fields[key_name])
            response['created'] = created

        return do_create(self, request)
