from django.test import TestCase

from mock import patch


class TestMiddleware(TestCase):
    def test_request(self):
        called = []
        def flush_cache(*a):
            called.append(True)
        with patch('slumber.connector.Client._flush_client_instance_cache', flush_cache):
            response = self.client.get('/')
        self.assertTrue(called)
