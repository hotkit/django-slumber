from mock import patch

from django.test import TestCase

from slumber.connector import Client


class TestServices(TestCase):
    def setUp(self):
        self.service = lambda: 'pizzas'
        self.services = lambda _ = None: {
            self.service(): 'http://localhost:8000:/slumber/pizzas/',
            'takeaway': 'http://localhost:8002:/slumber/'}
        self.__patchers = [
            patch('slumber.connector.get_slumber_service', self.service),
            patch('slumber.connector.get_slumber_directory', self.services),
            patch('slumber.connector.get_slumber_services', self.services),
            patch('slumber.server.views.get_slumber_service', self.service),
            patch('slumber.server.get_slumber_service', self.service),
            patch('slumber.server.get_slumber_directory', self.services),
        ]
        [p.start() for p in self.__patchers]
        self.client = Client() # We need a client set up after we patch the directory
        super(TestServices, self).setUp()

    def tearDown(self):
        [p.stop() for p in self.__patchers]


    def test_services_appear(self):
        self.assertTrue(hasattr(self.client, 'pizzas'))
        self.assertTrue(hasattr(self.client, 'takeaway'))
        self.assertFalse(hasattr(self.client, 'not-a-service'))


    def test_service_has_correct_directory_url(self):
        self.assertEqual(self.client.pizzas._directory,
            'http://localhost:8000:/slumber/pizzas/')


    def test_service_applications_appear(self):
        self.assertTrue(hasattr(self.client.pizzas, 'slumber_examples'))

