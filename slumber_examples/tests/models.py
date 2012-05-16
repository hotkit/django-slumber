from django.test import TestCase as DBTestCase
from mock import patch
from unittest2 import TestCase

from slumber import client
from slumber.connector import Client
from slumber.scheme import to_slumber_scheme, from_slumber_scheme, \
    SlumberServiceURLError

from slumber_examples.models import Shop, Order
from slumber_examples.tests.configurations import ConfigureUser
from slumber_examples.tests.views import ServiceTestsWithDirectory


class URLHandlingToDatabase(TestCase):
    def test_no_services_pass_url_unchanged(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/', None)
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_not_a_service(self):
        translated = to_slumber_scheme(
            'http://example.org/slumber/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.org/slumber/')

    def test_is_a_service(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/testservice/Model/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'slumber://testservice/Model/')

    def test_ambiguous_prefix(self):
        translated = to_slumber_scheme(
            'http://www.example.com/slumber/testservice/Model/',
            dict(a='http://www.example.com/slumber/testservice/',
                testmodel='http://www.example.com/slumber/testservice/Model/'))
        self.assertEquals(translated, 'slumber://testmodel/')


class URLHandlingFromDatabase(TestCase):
    def test_no_services_with_normal_url(self):
        translated = from_slumber_scheme(
            'http://example.com/slumber/', None)
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_no_services_with_slumber_url(self):
        with self.assertRaises(SlumberServiceURLError):
            translated = from_slumber_scheme(
                'slumber://service/Model/', None)

    def test_not_a_slumber_url(self):
        translated = from_slumber_scheme(
            'http://example.org/slumber/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.org/slumber/')

    def test_slumber_service_url(self):
        translated = from_slumber_scheme(
            'slumber://testservice/Model/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.com/slumber/testservice/Model/')

    def test_slumber_service_url_with_a_different_service(self):
        translated = from_slumber_scheme(
            'slumber://another_service/Model/',
            dict(testservice='http://example.com/slumber/testservice/',
                another_service='http://example.com/slumber/another_service/'))
        self.assertEquals(translated,
            'http://example.com/slumber/another_service/Model/')

    def test_slumber_service_url_with_invalid_service(self):
        with self.assertRaises(SlumberServiceURLError):
            from_slumber_scheme(
                'slumber://not-a-service/Model/',
                dict(testservice='http://example.com/slumber/testservice/'))


class TestQueries(ConfigureUser, ServiceTestsWithDirectory, DBTestCase):
    REAL_URL = 'http://localhost:8000/slumber/pizzas/slumber_examples/Shop/data/1/'
    SLUMBER_URL = 'slumber://pizzas/slumber_examples/Shop/data/1/'

    def setUp(self):
        super(TestQueries, self).setUp()
        self.shop = Shop(name='Test', slug='test', active=True)
        self.shop.save()

    def test_have_shop(self):
        with patch('slumber._client', Client()):
            shop = client.pizzas.slumber_examples.Shop.get(pk=1)
            self.assertEqual(shop._url, self.REAL_URL)

    def test_find_order_by_shop_remote_instance(self):
        with patch('slumber._client', Client()):
            shop = client.pizzas.slumber_examples.Shop.get(pk=1)
            order = Order(shop=shop)
            order.save()
            fetched = Order.objects.get(shop=shop)
            self.assertEqual(order, fetched)

    def test_find_order_by_shop_url(self):
        with patch('slumber._client', Client()):
            shop = client.pizzas.slumber_examples.Shop.get(pk=1)
            order = Order(shop=shop)
            order.save()
            fetched = Order.objects.get(shop=self.SLUMBER_URL)
            self.assertEqual(order, fetched)

