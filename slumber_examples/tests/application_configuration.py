from django.test import TestCase

from slumber import client, configure
from slumber.server.application import DjangoApp

from slumber_examples.models import Shop

from views import _perform


class TestSlumberConfiguration(TestCase):
    def test_shop_class_appears(self):
        self.assertTrue(hasattr(client.slumber_examples, 'Shop'),
            client.slumber_examples.__dict__.keys())

    def test_shop_model_has_web_address_property(self):
        response, json = _perform(self.client, 'get',
            '/slumber/slumber_examples/Shop/', {})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('web_address'), json['fields'].keys())
        self.assertEquals(json['fields']['web_address']['kind'], 'property')
        self.assertEquals(json['fields']['web_address']['type'],
            'slumber_examples.Shop.web_address')
        self.assertTrue(json['fields']['web_address']['readonly'])

    def test_shop_instance_has_web_address(self):
        shop = Shop(name='Test', slug='test')
        shop.save()
        self.assertEquals(shop.web_address,
            'http://www.example.com/test/')
        rshop = client.slumber_examples.Shop.get(pk=shop.pk)
        self.assertEquals(rshop.slug, 'test')
        self.assertEquals(rshop.web_address,
            'http://www.example.com/test/')

    def test_to_json_configuration(self):
        shop = Shop(name='Test', slug='test')
        shop.save()
        configure(Shop,
            to_json = {
                'slumber_examples.Shop.web_address':
                    lambda r, m, i, fm, v: v.replace('http:', 'https:')
                })
        rshop = client.slumber_examples.Shop.get(pk=shop.pk)
        self.assertEquals(rshop.slug, 'test')
        self.assertEquals(rshop.web_address,
            'https://www.example.com/test/')
        from slumber.server.json import DATA_MAPPING
        del DATA_MAPPING['slumber_examples.Shop.web_address']
