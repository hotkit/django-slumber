from slumber.operations import InstanceOperation


class OrderPizza(InstanceOperation):
    def get(self, request, response, app, model, pk):
        response['form'] = dict(
            quantity='integer')
