from slumber import configure


class ShopProxy(object):
    def has_shop_proxy(self):
        return True
configure('/slumber_examples/Shop/',
    model_proxy = ShopProxy)


class PizzaProxy(object):
    def has_pizza_proxy(self):
        return True
configure('/slumber_examples/Pizza/',
    instance_proxy = PizzaProxy)
