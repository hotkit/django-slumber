from django.test import TestCase
from slumber import client
from slumber.connector import Client, DictObject
from slumber_test.models import Pizza
from mock import patch

class TestGetUrl(TestCase):
    @patch('slumber.connector.Client._load_apps')
    def test_get_default_url_with_made_client(self, mocked_load_apps):
        client = Client()
        self.assertEqual('http://localhost:8000/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_default_url_with_default_client(self, mocked_load_apps):
        self.assertEqual('http://localhost:8000/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_url_of_google(self, mocked_load_apps):
        client = Client('http://www.google.com/')
        self.assertEqual('http://www.google.com/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_url_with_root(self, mocked_load_apps):
        client = Client()
        self.assertEqual('http://localhost:8000/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_some_url(self, mocked_load_apps):
        client = Client()
        self.assertEqual('http://localhost:8000/rooted_url/',
            client._get_url('/rooted_url/'))


class TestDoGet(TestCase):
    @patch('slumber.connector.Client._load_apps')
    def test_do_get(self, mocked_load_apps):
        """
        _do_get should return the dict of the result
        """
        response, json = client._do_get('/slumber')
        apps = json['apps']
        self.assertEquals(apps['slumber_test'], '/slumber/slumber_test/')


class TestLoads(TestCase):

    @patch('slumber.connector.Client._load_apps')
    def test_root_is_passed_in_load_apps(self, mocked_load_apps):
        client = Client('http://localhost:8000/slumber')
        args = (('http://localhost:8000/slumber',))
        mocked_load_apps.assert_called_with_args(args)

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
        (i.e. django.contrib.messages)
        """
        client = Client('http://localhost:8000/slumber')
        self.assertTrue(hasattr(client, 'django_contrib_sites'), client.__dict__.keys())

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
