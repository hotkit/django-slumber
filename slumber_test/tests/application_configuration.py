from django.test import TestCase

from slumber import client


class TestNested1Configuration(TestCase):
    def test_nest_class_appears(self):
        self.assertTrue(hasattr(client.slumber_test.nested1, 'Nest'),
            client.slumber_test.nested1.__dict__.keys())

