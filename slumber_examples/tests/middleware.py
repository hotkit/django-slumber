from django.conf import settings
from django.test import TestCase

from slumber import client
from slumber._caches import PER_THREAD
from slumber.connector.middleware import Cache

from slumber_examples.tests.client import TestsWithPizza
from slumber_examples.tests.configurations import ConfigureUser

from mock import patch


class _FailingMiddleware:
    def process_request(self, request):
        assert False, "This middleware is meant to fail."

class TestAddMiddleware(ConfigureUser, TestCase):
    def setUp(self):
        settings.MIDDLEWARE_CLASSES.append(
            'slumber_examples.tests.middleware._FailingMiddleware')
    def tearDown(self):
        settings.MIDDLEWARE_CLASSES.remove(
            'slumber_examples.tests.middleware._FailingMiddleware')

    def test_middleware_fails(self):
        with self.assertRaises(AssertionError):
            self.client.get('/')


# Repeat the TestsWithPizza with the middelware enabled
class TestMiddleware(TestsWithPizza):
    def setUp(self):
        self.middleware = Cache()
        self.middleware.process_request(None)
        super(TestMiddleware, self).setUp()

    def tearDown(self):
        super(TestMiddleware, self).tearDown()
        self.middleware.process_response(None, None)


    # TODO: The following test is broken until we can get the threading
    # done in such a way that all of this still works as it should
    #def test_alias_writes_are_visible(self):
        #m1 = client.slumber_examples.Pizza.get(pk=1)
        #m2 = client.slumber_examples.Pizza.get(pk=1)
        #self.assertEqual(m1.id, m2.id)
        #self.assertTrue(PER_THREAD.cache.get(m1._url, None),
        #(m1._url, PER_THREAD.cache.keys()))
        #with self.assertRaises(AttributeError):
            #m1.attr
        #with self.assertRaises(AttributeError):
            #m2.attr
        #m1.attr = 'attribute data'
        #self.assertEqual(m1.attr, 'attribute data')
        #self.assertEqual(m1.attr, m2.attr)


class TestSetting(ConfigureUser, TestCase):
    def test_request(self):
        middleware = Cache()
        middleware.process_request(None)
        self.assertTrue(hasattr(PER_THREAD, 'cache'))
        response = middleware.process_response(None, 'response')
        self.assertFalse(hasattr(PER_THREAD, 'cache'))
        self.assertEqual(response, 'response')

