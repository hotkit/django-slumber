from mock import patch
from unittest2 import TestCase

from slumber.connector.ua import post


class TestPost(TestCase):

    def test_fake(self):
        class response:
            status_code = 200
            content = "123"
        def _post(self, url, data, **kw):
            return response()
        with patch('slumber.connector.ua.FakeClient.post', _post):
            response, json = post('/local/', {})
        self.assertEqual(json, 123)

    def test_real(self):
        class response:
            status = 200
        def _request(_self, url, method, body):
            self.assertEqual(body, "data=23")
            return response(), "123"
        with patch('slumber.connector.ua.Http.request', _request):
            response, json = post('http://example.com/', {
                'data': 23})
        self.assertEqual(json, 123)
