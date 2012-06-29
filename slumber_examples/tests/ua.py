from django.core.cache import cache
from httplib2 import ServerNotFoundError
from mock import Mock, patch
import socket
from unittest2 import TestCase

from slumber.connector.ua import for_user, get, post
from slumber_examples.tests.views import ServiceTests


class _response_fake(object):
    status_code = 200
    content = '123'

class _response_httplib2(object):
    status = 200
    content = '123'


class TestPost(TestCase):
    def test_fake(self):
        def _post(self, url, data, **kw):
            return _response_fake()
        with patch('slumber.connector.ua.FakeClient.post', _post):
            response, json = post('/local/', {})
        self.assertEqual(json, 123)

    def test_real(self):
        def _request(_self, url, method, body, headers={}):
            self.assertEqual(body, '{"data": 23}')
            return _response_httplib2(), "123"
        with patch('slumber.connector.ua.Http.request', _request):
            response, json = post('http://example.com/', {
                'data': 23})
        self.assertEqual(json, 123)

    def test_404_allowed_for_fake(self):
        response, json = post('/slumber/does-not-exist/', {}, [404])
        self.assertEqual(response.status_code, 404)


class TestGet(TestCase):
    def setUp(self):
        self.cache_url = 'http://example.com'
    def tearDown(self):
        cache.delete('slumber.connector.ua.get.' + self.cache_url)

    def test_real(self):
        class response:
            status = 200
            content = '''{"apps":{}}'''
        def _request(_self, url, headers={}):
            r = response()
            return r, r.content
        with patch('slumber.connector.ua.Http.request', _request):
            response, json = get(self.cache_url)
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
        def _request(_self, url, headers={}):
            self.callers.append(_self)
            r = response()
            return r, r.content
        with patch('slumber.connector.ua.Http.request',_request):
            get(self.cache_url)
            get(self.cache_url)
            self.assertNotEqual(self.callers[0], self.callers[1])

    def test_get_retries(self):
        class _response:
            content = '''{"apps":{}}'''
            def __init__(self, counter):
                self.status = 200 if counter == 1 else 404
        counter = []
        def _request(_self, url, headers={}):
            r = _response(len(counter))
            counter.append(True)
            return r, r.content
        with patch('slumber.connector.ua.Http.request', _request):
            get(self.cache_url)
        self.assertEqual(len(counter), 2)

    def test_retry_get_still_can_fail(self):
        class _response:
            content = ''
            status = 500
        def _request(_self, url, headers={}):
            r = _response()
            return r, r.content
        with patch('slumber.connector.ua.Http.request',_request):
            with self.assertRaises(AssertionError):
                get(self.cache_url)

    def test_cache_ttl(self):
        def _request(_self, url, headers={}):
            r = _response_httplib2()
            return r, r.content
        with patch('slumber.connector.ua.Http.request', _request):
            get(self.cache_url, 2)
        with patch('slumber.connector.ua.Http.request', self.fail):
            get(self.cache_url, 2)

    def test_cache(self):
        try:
            r1, j1 = get('http://urquell-fn.appspot.com/lib/echo/?__=', 2)
            r2, j2 = get('http://urquell-fn.appspot.com/lib/echo/?__=', 2)
            r3, j3 = get('http://urquell-fn.appspot.com/lib/echo/?dummy=&__=', 2)
            self.assertFalse(hasattr(r1, 'from_cache'))
            self.assertTrue(hasattr(r2, 'from_cache'))
            self.assertTrue(r2.from_cache)
            self.assertFalse(hasattr(r3, 'from_cache'))
        except ServerNotFoundError:
            # If we get a server error then we presume that there is no good
            # Internet connection and don't fail the test
            pass
        except socket.error:
            pass
        except Exception, e:
            print type(e)
            raise e


class TestUsernameDecorator(ServiceTests, TestCase):
    def setUp(self):
        super(TestUsernameDecorator, self).setUp()
        self.checked = False

    def signature_with_username(self, authn_name, method, url,
            body, username, for_fake_client):
        self.checked = True
        self.assertEqual(username, 'test-user')
        return {}

    def test_post_uses_username(self):
        @for_user('test-user')
        def do_post():
            with patch('slumber.connector.ua._calculate_signature',
                    self.signature_with_username):
                post('/slumber/', {})
        do_post()
        self.assertTrue(self.checked)

    def test_get_uses_username(self):
        @for_user('test-user')
        def do_get():
            with patch('slumber.connector.ua._calculate_signature',
                    self.signature_with_username):
                get('/slumber/')
        do_get()
        self.assertTrue(self.checked)

