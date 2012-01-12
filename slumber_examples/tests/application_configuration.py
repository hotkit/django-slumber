from django.test import TestCase

from slumber import client
from slumber.server.application import DjangoApp


class TestSlumberConfiguration(TestCase):
    def test_shop_class_appears(self):
        self.assertTrue(hasattr(client.slumber_examples, 'Shop'),
            client.slumber_examples.__dict__.keys())

