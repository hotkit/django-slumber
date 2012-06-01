import copy
from decimal import Decimal
import logging
import mock
import unittest2

from django.http import HttpResponse
import django.test

from slumber import client
from slumber.test import mock_client

from slumber_examples.models import Order
from slumber_examples.tests.views import ServiceTestsWithDirectory


class TestSlumberMock(unittest2.TestCase):
    margarita = dict(pk=1, name='Margarita', for_sale=True)


    @mock_client(app__contrib__auth__Model=[], app__Pizza=[])
    def test_basic_app_data(self):
        """Ensure that the basic meta data part of the mock works as it should.
        """
        self.assertTrue(hasattr(client, 'app'))
        self.assertTrue(hasattr(client.app, 'contrib'))
        self.assertTrue(hasattr(client.app.contrib, 'auth'))
        self.assertTrue(hasattr(client.app.contrib.auth, 'Model'))
        self.assertTrue(hasattr(client.app, 'Pizza'))
        self.assertFalse(hasattr(client, 'slumber'))


    @mock_client(
        slumber__Pizza=[
           margarita,
            dict(pk=2, name='Four seasons', prices=[
                dict(pk=2, amount=Decimal("13"))
            ]),
            dict(pk=3, name='Hawaiin', for_sale=False),
        ],
        slumber__PizzaPrice= [
            dict(pk=1,
                pizza=margarita,
                date='2010-01-01', amount=Decimal("14")),
        ])
    def test_get_pizza(self):
        """Ensure that we can manage instances and data arrays properly.
        """
        p1 = client.slumber.Pizza.get(pk=1)
        self.assertEquals(p1.pk, 1)
        self.assertEquals(getattr(p1, 'name', None), 'Margarita', p1.__dict__)
        self.assertEquals(type(p1).__name__, "slumber/Pizza/")

        p2 = client.slumber.Pizza.get(pk=2)
        self.assertEquals(p2.pk, 2)
        self.assertEquals(len(p2.prices), 1)
        self.assertTrue(hasattr(p2.prices[0], 'pk'), type(p2.prices[0]))
        self.assertEquals(p2.prices[0].amount, Decimal("13"))

        pp1 = client.slumber.PizzaPrice.get(pk=1)
        self.assertEquals(pp1.pk, 1)
        self.assertEquals(pp1.pizza.name, 'Margarita')


    @mock_client(django__contrib__auth__User=[])
    def test_not_found_asserts(self):
        with self.assertRaises(AssertionError):
            client.django.contrib.auth.User.get(pk=1)

    @mock_client(django__contrib__auth__User=[])
    def test_model_proxy_is_applied(self):
        self.assertTrue(hasattr(client.django.contrib.auth.User, 'authenticate'))

    @mock_client(app__Model=[
        dict(pk=1)
    ])
    def test_aliase_writes_are_visible(self):
        m1 = client.app.Model.get(pk=1)
        m2 = client.app.Model.get(pk=1)
        self.assertEqual(m1.pk, m2.pk)
        with self.assertRaises(AttributeError):
            m1.attr
        with self.assertRaises(AttributeError):
            m2.attr
        m1.attr = 'attribute data'
        self.assertEqual(m1.attr, 'attribute data')
        self.assertEqual(m1.attr, m2.attr)


class TestMockWithDatabase(ServiceTestsWithDirectory, django.test.TestCase):
    def _setup(self):
        # Can't use setUp as that runs before the mock is applied
        self.shop = client.pizzas.slumber_examples.Shop.get(pk=1)
        self.order = Order(shop=self.shop)
        self.order.save()
        for order in Order.objects.all():
            logging.debug(order.shop)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1, _url='slumber://pizzas/slumber_examples/Shop/data/1/')
    ])
    def test_can_order_with_remote_shop_mock(self):
        self._setup()
        fetched = Order.objects.get(shop=self.shop)
        self.assertEqual(self.order, fetched)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1, _url='slumber://pizzas/slumber_examples/Shop/data/1/')
    ])
    def test_can_order_with_remote_shop_url(self):
        self._setup()
        fetched = Order.objects.get(
            shop='slumber://pizzas/slumber_examples/Shop/data/1/')
        self.assertEqual(self.order, fetched)


class TestViews(django.test.TestCase):
    @mock_client()
    def test_view(self):
        """Make sure that a simple view works with the mocked client.
        """
        self.client.get('/')

    @mock_client()
    @mock.patch('slumber_examples.views.ok_text')
    def test_mocked_then_patched(self, ok_text_patch):
        ok_text_patch.return_value = HttpResponse('patched')
        self.client.get('/')

    @mock.patch('slumber_examples.views.ok_text')
    @mock_client()
    def test_patched_then_mocked(self, ok_text_patch):
        ok_text_patch.return_value = HttpResponse('patched')
        self.client.get('/')


class TestCopy(ServiceTestsWithDirectory, django.test.TestCase):
    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_deepcopy_shop(self):
        shop = client.pizzas.slumber_examples.Shop.get(pk=1)
        deep = copy.deepcopy(shop)
        self.assertEqual(shop.pk, deep.pk)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_deepcopy_shop_in_order_query(self):
        query = Order.objects.filter(
            shop='slumber://pizzas/slumber_examples/Shop/data/1/')
        self.assertEqual(query.count(), 0)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_deepcopy_shop_in_order_query_double_filter_client_shop(self):
        shop = client.pizzas.slumber_examples.Shop.get(pk=1)
        query1 = Order.objects.filter(shop=shop)
        self.assertEqual(query1.count(), 0)
        query2 = query1.exclude(shop=shop)
        self.assertEqual(query2.count(), 0)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_deepcopy_shop_in_order_query_double_filter_shop_url(self):
        shop = 'slumber://pizzas/slumber_examples/Shop/data/1/'
        query1 = Order.objects.filter(shop=shop)
        self.assertEqual(query1.count(), 0)
        query2 = query1.exclude(shop=shop)
        self.assertEqual(query2.count(), 0)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_deepcopy_shop_in_order_query_double_filter_shop_from_order(self):
        order = Order.objects.create(
            shop = 'slumber://pizzas/slumber_examples/Shop/data/1/')
        query1 = Order.objects.filter(shop=order.shop)
        self.assertEqual(query1.count(), 1)
        query2 = query1.filter(shop=order.shop)
        self.assertEqual(query2.count(), 1)
