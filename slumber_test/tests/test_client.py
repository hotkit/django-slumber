from django.test import TestCase
from slumber import client
from slumber.connector import Client, DictObject
from slumber_test.models import Pizza
from mock import patch

class TestDirectoryURLs(TestCase):
    def test_get_default_url_with_made_client(self):
        client = Client()
        self.assertEqual('http://localhost:8000/slumber/', client._directory)

    def test_get_default_url_with_default_client(self):
        self.assertEqual('http://localhost:8000/slumber/', client._directory)


class TestLoads(TestCase):

    def test_applications_local(self):
        client = Client('http://localhost:8000/slumber')
        self.assertTrue(hasattr(client, 'slumber_test'))

    def test_applications_remote(self):
        def request(k, u):
            self.assertEquals(u, 'http://slumber.example.com/')
            return DictObject(status=200), '''{"apps":{}}'''
        with patch('slumber.connector.ua.Http.request', request):
            client = Client('http://slumber.example.com/')

    def test_applications_with_dots_in_name(self):
        """
        dots (.) will be replaced with underscores (_) for some apps that may have dots in its name
        (i.e. django.contrib.sites)
        """
        client = Client()
        self.assertTrue(hasattr(client, 'django'), client.__dict__.keys())
        self.assertTrue(hasattr(client.django, 'contrib'), client.django.__dict__.keys())
        self.assertTrue(hasattr(client.django.contrib, 'sites'),
            (type(client.django.contrib), client.django.contrib.__dict__.keys()))

    def test_instance_data(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        pizza = client.slumber_test.Pizza.get(pk=s.pk)
        self.assertEqual('S1', pizza.name)
        prices = pizza.prices
        self.assertEqual(len(prices), 0)
        with self.assertRaises(AttributeError):
            pizza.not_a_field

    def test_instance_no_pk(self):
        pizza = client.slumber_test.Pizza.get(pk=None)
        self.assertTrue(pizza is None)
