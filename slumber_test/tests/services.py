from django.test import TestCase

from slumber.connector import Client


class TestServices(TestCase):
    def setUp(self):
        pizzas = lambda: 'pizzas'
        self.__patchers = [
            patch('slumber.server.views.get_slumber_service', pizzas),
            patch('slumber.server.get_slumber_service', pizzas),
        ]
        [p.start() for p in self.__patchers]
        self.client = Client() # We need a client set up after we patch the directory
        super(TestServices, self).setUp()

    def tearDown(self):
        [p.stop() for p in self.__patchers]

