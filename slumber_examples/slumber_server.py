from slumber import configure
from slumber.operations.instancedata import InstanceData

from models import Pizza, Shop
from operations import OrderPizza, ShopList


configure(
    {'test': True})

configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    operations_extra = [
        (ShopList, 'shops1', 'shops/mount1'),
        (InstanceData, 'instance', 'shop')],
    properties_ro = ['web_address'])
