from slumber import configure
from slumber.operations.instancedata import InstanceData
from slumber.operations.instancelist import InstanceListHal

from models import Pizza, Shop
from operations import OrderPizza, ShopList


configure(
    {'test': True})

configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    operations_extra = [
        (None, 'delete'),
        (ShopList, 'shops1', 'shops/mount1'),
        (InstanceListHal, 'shops-hal', 'shops/mount2'),
        (InstanceData, 'data', 'pizzas/shop'),
    ],
    properties_ro = ['web_address'])
