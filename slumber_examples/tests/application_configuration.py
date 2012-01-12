from django.test import TestCase

from slumber import client
from slumber.server.application import DjangoApp

from views import _perform


class TestSlumberConfiguration(TestCase):
    def test_shop_class_appears(self):
        self.assertTrue(hasattr(client.slumber_examples, 'Shop'),
            client.slumber_examples.__dict__.keys())

    def test_shop_has_web_address_property(self):
        response, json = _perform(self.client, 'get',
            '/slumber/slumber_examples/Shop/', {})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('web_address'), json['fields'].keys())
        self.assertEquals(json['fields']['web_address']['kind'], 'property')
        self.assertTrue(json['fields']['web_address']['readonly'])
