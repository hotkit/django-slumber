from django.test import TestCase
from slumber.client import Client

class TestClient(TestCase):
        
    def test_get_default_url(self):
        client = Client()
        self.assertEqual('http://localhost/', client._get_url())

    def test_get_url_of_google(self):
        client = Client('www.google.com')
        self.assertEqual('http://www.google.com/', client._get_url())
        
    def test_get_url_with_root(self):
        client = Client(root='/slumber')
        self.assertEqual('http://localhost/slumber/', client._get_url())

    def test_get_some_url(self):
        client = Client(root='/slumber')
        self.assertEqual('http://localhost/slumber/slumber_test', client._get_url('/slumber_test'))

    def test_applications(self):
        client = Client()
        self.assertTrue(client.slumber_test)
        self.assertTrue(client.django_contrib_messages)


class TestDoGet(TestCase):

    def test_do_get(self):
        """
        _do_get should return the dict of the result
        """
        client = Client('localhost:8003', '/slumber')
        response, json = client._do_get('/')
        apps = json['apps']
        self.assertEquals(apps['slumber_test'], '/slumber/slumber_test/')

