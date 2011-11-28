from mock import Mock, patch
from unittest2 import TestCase

from slumber.connector.ua import get, post


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

class TestGet(TestCase):

    def test_real(self):
        class response:
            status = 200
            content = '''{"apps":{}}'''
        def _request(_self, url):
            r = response()
            return r, r.content
        with patch('slumber.connector.ua.Http.request', _request):
            response, json = get('http://example.com/')
        self.assertEqual(json, {"apps":{}})

    def test_real_does_not_use_cached_httplib2_client(self):
        """
        When we use this slumber in Wimbledon project, we found that the request
        is occationally error on IE9 (got 500 response in return bcoz of the empty
        request). We are not sure if the root cause was in IE9 or in the httplib2,
        but stop caching httplib2's client fixed it (reset client everytime).

        The downside is we cannot use caching features of the httplib2's client,
        but until we understand this problem in more details, we'll stick with
        resetting client every time.

        juacompe, 2nd November 2011

        ref: http://proteus.eidos.proteus-tech.com/project/BBG/story/BBG-251/card/
        """
        self.callers = []
        class response:
            status = 200
            content = '''{"apps":{}}'''
        def _request(_self, url):
            self.callers.append(_self)
            r = response()
            return r, r.content
        with patch('slumber.connector.ua.Http.request',_request):
            get('http://example.com/')
            get('http://example.com/')
            self.assertNotEqual(self.callers[0], self.callers[1])

    def test_get_retries(self):
        class _response:
            content = '''{"apps":{}}'''
            def __init__(self, counter):
                self.status = 200 if counter == 1 else 404
        counter = []
        def _request(_self, url):
            r = _response(len(counter))
            counter.append(True)
            return r, r.content
        with patch('slumber.connector.ua.Http.request',_request):
            get('http://example.com')
        self.assertEqual(len(counter), 2)


    def test_retry_get_still_can_fail(self):
        class _response:
            content = ''
            status = 500
        def _request(_self, url):
            r = _response()
            return r, r.content
        with patch('slumber.connector.ua.Http.request',_request):
            with self.assertRaises(AssertionError):
                get('http://example.com')
