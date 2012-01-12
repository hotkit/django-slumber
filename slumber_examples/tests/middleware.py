from django.conf import settings
from django.test import TestCase

from slumber import client
from slumber.connector.middleware import Cache

from slumber_examples.tests.client import TestsWithPizza

from mock import patch


class _FailingMiddleware:
    def process_request(self, request):
        assert False, "This middleware is meant to fail."

class TestAddMiddleware(TestCase):
    def setUp(self):
        settings.MIDDLEWARE_CLASSES.append(
            'slumber_examples.tests.middleware._FailingMiddleware')
    def tearDown(self):
        settings.MIDDLEWARE_CLASSES.remove(
            'slumber_examples.tests.middleware._FailingMiddleware')

    def test_middleware_fails(self):
        with self.assertRaises(AssertionError):
            self.client.get('/')


class TestMiddleware(TestsWithPizza):
    def setUp(self):
        self.middleware = Cache()
        self.middleware.process_request(None)
        super(TestMiddleware, self).setUp()

    def tearDown(self):
        super(TestMiddleware, self).tearDown()
        self.middleware.process_response(None, None)


    def test_alias_writes_are_visible(self):
        m1 = client.slumber_examples.Pizza.get(pk=1)
        m2 = client.slumber_examples.Pizza.get(pk=1)
        self.assertEqual(m1.id, m2.id)
        with self.assertRaises(AttributeError):
            m1.attr
        with self.assertRaises(AttributeError):
            m2.attr
        m1.attr = 'attribute data'
        self.assertEqual(m1.attr, 'attribute data')
        self.assertEqual(m1.attr, m2.attr)


class TestSetting(TestCase):
    def test_request(self):
        called = []
        def flush_cache(*a):
            called.append(True)
        middleware = Cache()
        middleware.process_request(None)
        with patch('slumber.connector.Client._flush_client_instance_cache', flush_cache):
            response = middleware.process_response(None, 'response')
        self.assertTrue(called)
        self.assertEqual(response, 'response')

