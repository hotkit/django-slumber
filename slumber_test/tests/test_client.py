from django.test import TestCase
from slumber.connector import Client, DictObject
from slumber_test.models import Pizza
from mock import patch

class TestGetUrl(TestCase):
    @patch('slumber.connector.Client._load_apps')
    def test_get_default_url(self, mocked_load_apps):
        client = Client()
        self.assertEqual('http://localhost/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_url_of_google(self, mocked_load_apps):
        client = Client('www.google.com')
        self.assertEqual('http://www.google.com/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_url_with_root(self, mocked_load_apps):
        client = Client()
        self.assertEqual('http://localhost/', client._get_url())

    @patch('slumber.connector.Client._load_apps')
    def test_get_some_url(self, mocked_load_apps):
        client = Client()
        self.assertEqual('http://localhost/slumber_test/', client._get_url('/slumber_test/'))


class TestDoGet(TestCase):
    @patch('slumber.connector.Client._load_apps')
    def test_do_get(self, mocked_load_apps):
        """
        _do_get should return the dict of the result
        """
        client = Client('localhost:8000')
        response, json = client._do_get('/slumber')
        apps = json['apps']
        self.assertEquals(apps['slumber_test'], '/slumber/slumber_test/')


class TestLoads(TestCase):

    @patch('slumber.connector.Client._load_apps')
    def test_root_is_passed_in_load_apps(self, mocked_load_apps):
        client = Client(root='/slumber')
        args = (('/slumber',))
        mocked_load_apps.assert_called_with_args(args)

    def test_applications_local(self):
        client = Client('localhost:8000', '/slumber')
        self.assertTrue(hasattr(client, 'slumber_test'))

    def test_applications_remote(self):
        def request(k, u):
            self.assertEquals(u, 'http://slumber.example.com/')
            return DictObject(status=200), '''{"apps":{}}'''
        with patch('slumber.connector.Http.request', request):
            client = Client('slumber.example.com', '/')

    def test_applications_with_dots_in_name(self):
        """
        dots (.) will be replaced with underscores (_) for some apps that may have dots in its name
        (i.e. django.contrib.messages)
        """
        client = Client('localhost:8000', '/slumber')
        self.assertTrue(hasattr(client, 'django_contrib_sites'), client.__dict__.keys())

    def test_instance_data(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        client = Client('localhost:8000', '/slumber')
        pizza = client.slumber_test.Pizza.get(pk=s.pk)
        self.assertEqual('S1', pizza.name)

    def test_instance_no_pk(self):
        client = Client('localhost:8000', '/slumber')
        pizza = client.slumber_test.Pizza.get(pk=None)
        self.assertTrue(pizza is None)
