from slumber.operations import InstanceOperation, ModelOperation


class OrderPizza(InstanceOperation):
    def get(self, request, response, app, model, pk):
        response['form'] = dict(quantity='integer')

    def post(self, _request, _response, _app, _model, _pk):
        raise NotImplementedError("OrderPizza.post")


class ShopList(ModelOperation):
    def get(self, _request, response, _app, _model):
        response['shops'] = [{
                'name': 'Hard Coded Pizza Parlour'
            }]

