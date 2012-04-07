from mock import patch

from django.test import TestCase

from slumber.connector import Client, ServiceConnector

from slumber_examples.tests.configurations import ConfigureUser


class TestServices(ConfigureUser, TestCase):
    def setUp(self):
        self.service_name = lambda: 'pizzas'
        self.services = lambda _ = None: {
            self.service_name(): 'http://localhost:8000:/slumber/pizzas/',
            'takeaway': 'http://localhost:8002:/slumber/'}
        self.__patchers = [
            patch('slumber.server._get_slumber_directory', self.services),
            patch('slumber.server._get_slumber_service', self.service_name),
        ]
        [p.start() for p in self.__patchers]
        self.cnx = Client() # We need a client set up after we patch the directory
        super(TestServices, self).setUp()

    def tearDown(self):
        super(TestServices, self).tearDown()
        [p.stop() for p in self.__patchers]


    def test_services_appear(self):
        self.assertTrue(hasattr(self.cnx, 'pizzas'))
        self.assertTrue(hasattr(self.cnx, 'takeaway'))
        self.assertFalse(hasattr(self.cnx, 'not-a-service'))

    def test_service_has_correct_directory_url(self):
        self.assertEqual(self.cnx.pizzas._directory,
            'http://localhost:8000:/slumber/pizzas/')

    def test_service_applications_appear(self):
        self.assertTrue(
            isinstance(self.cnx.pizzas, ServiceConnector),
            type(self.cnx.pizzas))
        self.cnx.pizzas.slumber_examples
        self.assertTrue(
            hasattr(self.cnx.pizzas, 'slumber_examples'),
            self.cnx.pizzas.__dict__)

