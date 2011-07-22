from django.test import TestCase
from slumber.client import Client

class TestClient(TestCase):
        
    def test_applications(self):
        client = Client()
        self.assertTrue(client.slumber_test)
        self.assertTrue(client.django_contrib_messages)


class TestDoGet(TestCase):

    def test_do_get(self):
        """
        _do_get should return the dict of the result
        """
        client = Client('localhost:8003')
        response, json = client._do_get('/slumber/')
        apps = json['apps']
        self.assertEquals(apps['slumber_test'], '/slumber/slumber_test/')
