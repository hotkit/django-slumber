from django.test import TestCase

from slumber import client
from slumber.server.application import DjangoApp


class TestNested1Configuration(TestCase):
    def test_nest_class_appears(self):
        app = DjangoApp('slumber_test.nested1')
        self.assertTrue(hasattr(client.shop, 'Nest'),
            client.shop.__dict__.keys())

