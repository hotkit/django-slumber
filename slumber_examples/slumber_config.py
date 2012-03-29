from slumber import configure

from models import Pizza, Shop
from operations import OrderPizza
from proxies import PizzaProxy, ShopProxy


configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    properties_ro = ['web_address'])

configure('/slumber_examples/Pizza/',
    instance_proxy = PizzaProxy)

configure('/slumber_examples/Shop/',
    model_proxy = ShopProxy)
