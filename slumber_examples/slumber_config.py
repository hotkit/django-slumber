from slumber import configure

from models import Shop


configure(Shop,
    properties_ro = ['web_address'])

