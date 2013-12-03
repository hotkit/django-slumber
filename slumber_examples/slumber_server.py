from slumber import configure

from models import Pizza, Shop
from operations import OrderPizza, ShopList


configure(
    {'test': True})

configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    operations_extra = [(ShopList, 'shops', '/shops')],
    properties_ro = ['web_address'])
