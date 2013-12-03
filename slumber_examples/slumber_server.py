from slumber import configure

from models import Pizza, Shop
from operations import OrderPizza, ShopList


configure(
    {'test': True})

configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    operations_extra = [(ShopList, 'shops1', 'shops/mount1')],
    properties_ro = ['web_address'])
