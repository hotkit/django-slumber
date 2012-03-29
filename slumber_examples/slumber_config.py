from slumber import configure

from models import Pizza, Shop
from operations import OrderPizza
from proxies import PizzaProxy, ShopProxy


configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    properties_ro = ['web_address'])

configure('/Pizza/',
    instance_proxy = PizzaProxy)

configure('/Shop/',
    model_proxy = ShopProxy)
