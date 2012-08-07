import copy
from datetime import date
from decimal import Decimal
import logging
import mock
import unittest2

from django.contrib.auth.models import User
from django.http import HttpResponse
import django.test

from slumber import client
from slumber.connector.ua import get, post
from slumber.test import mock_client, mock_ua

from slumber_examples.models import Order
from slumber_examples.tests.views import ServiceTestsWithDirectory


class TestSlumberMockClient(ServiceTestsWithDirectory, unittest2.TestCase):
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
        pizzas__slumber__Pizza=[
           margarita,
            dict(pk=2, name='Four seasons', prices=[
                dict(pk=2, amount=Decimal("13"))
            ]),
            dict(pk=3, name='Hawaiin', for_sale=False),
            dict(id=4, name='Diablo', for_sale=True),
        ],
        pizzas__slumber__PizzaPrice= [
            dict(pk=1,
                pizza=margarita,
                date='2010-01-01', amount=Decimal("14")),
        ])
    def test_get_pizza(self):
        """Ensure that we can manage instances and data arrays properly.
        """
        p1 = client.pizzas.slumber.Pizza.get(pk=1)
        self.assertEquals(p1.pk, 1)
        self.assertEquals(getattr(p1, 'name', None), 'Margarita', p1.__dict__)
        self.assertEquals(type(p1).__name__, "slumber://pizzas/slumber/Pizza/data/1/")

        p2 = client.pizzas.slumber.Pizza.get(pk=2)
        self.assertEquals(p2.pk, 2)
        self.assertEquals(len(p2.prices), 1)
        self.assertTrue(hasattr(p2.prices[0], 'pk'), type(p2.prices[0]))
        self.assertEquals(p2.prices[0].amount, Decimal("13"))

        pp1 = client.pizzas.slumber.PizzaPrice.get(pk=1)
        self.assertEquals(pp1.pk, 1)
        self.assertEquals(pp1.pizza.name, 'Margarita')

        p3 = client.pizzas.slumber.Pizza.get(id=4)
        self.assertEqual(type(p3).__name__, "slumber://pizzas/slumber/Pizza/data/4/")
        self.assertEqual(p3.name, "Diablo")
        with self.assertRaises(AttributeError):
            p3.prices

    @mock_client(pizzas__slumber__Pizza=[dict(pk = 3, name = 'Hawaiin', for_sale = False)])
    def test_update_pizza(self):
        """Ensure that we can update instances data properly."""

        Hawaiin_pizza =  client.pizzas.slumber.Pizza.get(pk = 3)
        self.assertEquals(Hawaiin_pizza.for_sale, False)

        client.pizzas.slumber.Pizza.update(Hawaiin_pizza, for_sale = True)

        Hawaiin_pizza =  client.pizzas.slumber.Pizza.get(pk = 3)
        self.assertEquals(Hawaiin_pizza.for_sale, True)
        
    @mock_client(pizzas__app__Model=[])
    def test_created_object_can_be_gotten(self):
        client.pizzas.app.Model.create(id=1, name='Test')
        item = client.pizzas.app.Model.get(id=1)
        self.assertEqual(item.name, 'Test')

    @mock_client(django__contrib__auth__User=[])
    def test_not_found_asserts(self):
        with self.assertRaises(AssertionError):
            client.django.contrib.auth.User.get(pk=1)

    @mock_client(pizzas__app__Model=[
        dict(pk=1)
    ])
    def test_alias_writes_are_visible(self):
        m1 = client.pizzas.app.Model.get(pk=1)
        m2 = client.pizzas.app.Model.get(pk=1)
        self.assertEqual(m1.pk, m2.pk)
        with self.assertRaises(AttributeError):
            m1.attr
        with self.assertRaises(AttributeError):
            m2.attr
        m1.attr = 'attribute data'
        self.assertEqual(m1.attr, 'attribute data')
        self.assertEqual(m1.attr, m2.attr)

    @mock_client(app__Model=[])
    def test_model_operation_url_is_correct(self):
        self.assertEqual(client.app.Model._operations['test-op'],
            'http://app/Model/test-op/')

    @mock_client(pizzas__app__Model=[
        dict(pk=1)
    ])
    def test_instance_operation_url_is_correct(self):
        model = client.pizzas.app.Model.get(pk=1)
        self.assertEqual(model._operations['test-op'],
            'http://pizzas/app/Model/test-op/1/')


class TestSlumberMockUA(ServiceTestsWithDirectory, unittest2.TestCase):
    @mock_ua
    def test_empty_mock_ua_with_no_activity(self, expect):
        pass

    @unittest2.expectedFailure
    @mock_ua
    def test_unmet_expectation(self, expect):
        expect.get('/', {})

    @unittest2.expectedFailure
    @mock_ua
    def test_no_get_expectation(self, expect):
        get('/')

    @unittest2.expectedFailure
    @mock_ua
    def test_get_with_wrong_query(self, expect):
        expect.get('/?query1', {})
        get('/?another')

    @unittest2.expectedFailure
    @mock_ua
    def test_no_post_expectation(self, expect):
        post('/', {})

    @unittest2.expectedFailure
    @mock_ua
    def test_no_expectated_get_got_post(self, expect):
        expect.get('/', {})
        post('/', {})

    @unittest2.expectedFailure
    @mock_ua
    def test_no_expectated_post_got_get(self, expect):
        expect.post('/', {}, {})
        get('/')

    @mock_client(pizzas__app__Model=[])
    @mock_ua
    def test_model_operation_with_mock_ua(self, expect):
        expect.get('http://pizzas/app/Model/test-op/', {'test': 'item'})
        expect.post('http://pizzas/app/Model/test-op/', {'test': 'item'}, {'item': 'test'})
        self.assertEqual(len(expect.expectations), 2)
        response1, json1 = get(client.pizzas.app.Model._operations['test-op'])
        self.assertEqual(json1, dict(test='item'))
        response2, json2 = post(client.pizzas.app.Model._operations['test-op'], json1)
        self.assertEqual(json2, dict(item='test'))

    @mock_client(pizzas__django__contrib__auth__User=[
        dict(pk=1)])
    @mock_ua
    def test_instance_operation_with_mock_ua(self, expect):
        user = client.pizzas.django.contrib.auth.User.get(pk=1)
        expect.get(
            'http://pizzas/django/contrib/auth/User/has-permission/1/some.permission',
            {'is-allowed': True})
        has = user.has_perm('some.permission')
        self.assertTrue(has)


class TestMockWithDatabase(ServiceTestsWithDirectory, django.test.TestCase):
    def _setup(self):
        # Can't use setUp as that runs before the mock is applied
        self.shop = client.pizzas.slumber_examples.Shop.get(pk=1)
        self.order = Order(shop=self.shop)
        self.order.save()
        for order in Order.objects.all():
            logging.debug(order.shop)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_can_order_with_remote_shop_mock(self):
        self._setup()
        fetched = Order.objects.get(shop=self.shop)
        self.assertEqual(self.order, fetched)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_can_order_with_remote_shop_url(self):
        self._setup()
        fetched = Order.objects.get(
            shop='slumber://pizzas/slumber_examples/Shop/data/1/')
        self.assertEqual(self.order, fetched)

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1, slug='test-shop-1')
    ])
    def test_order_shop_finds_mock(self):
        self._setup()
        self.assertEqual(self.order.shop.pk, 1)
        self.assertEqual(self.order.shop.slug, 'test-shop-1')

    @mock_client(pizzas__django__contrib__auth__User=[{
            'pk': 1, 'id': 1, 'username': 'test-user-1',
                'is_active': True, 'is_staff': False, 'is_superuser': False,
                'date_joined': date(2011, 05, 23),
                'first_name': 'test1', 'last_name': 'user', 'email': 'test-user-1@example.com'
        }, {
            'pk': 2, 'id': 2, 'username': 'test-user-2',
                'is_active': True, 'is_staff': False, 'is_superuser': False,
                'date_joined': date(2011, 05, 23),
                'first_name': 'test2', 'last_name': 'user', 'email': 'test-user-2@example.com'
        }])
    def test_model_proxy_is_applied(self):
        self.assertTrue(hasattr(client.pizzas.django.contrib.auth.User, 'authenticate'))
        def post(url, data):
            self.assertEqual(url,
                'http://pizzas/django/contrib/auth/User/authenticate/')
            return None, {'authenticated': True, 'user': {
                'url': 'slumber://pizzas/django/contrib/auth/User/data/2/',
                    'display_name': 'test2 user'}}
        with mock.patch('slumber.connector.proxies.post', post):
            user = client.pizzas.django.contrib.auth.User.authenticate()
            self.assertEqual(user, User.objects.get(username='test-user-2'))

    @mock_client(pizzas__django__contrib__auth__User=[{
            'pk': 1, 'id': 1, 'username': 'test-user-1',
                'is_active': True, 'is_staff': False, 'is_superuser': False,
                'date_joined': date(2011, 05, 23),
                'first_name': 'test1', 'last_name': 'user', 'email': 'test-user-1@example.com'
        }, {
            'pk': 2, 'id': 2, 'username': 'test-user-2',
                'is_active': True, 'is_staff': False, 'is_superuser': False,
                'date_joined': date(2011, 05, 23),
                'first_name': 'test2', 'last_name': 'user', 'email': 'test-user-2@example.com'
        }])
    def test_instance_proxy_is_applied_using_mocked_get(self):
        user = client.pizzas.django.contrib.auth.User.get(pk=2)
        self.assertTrue(hasattr(user, 'has_perm'), type(user).__mro__)


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

    @mock_client(pizzas__slumber_examples__Shop = [
        dict(pk=1)
    ])
    def test_query_with_real_url(self):
        order = Order.objects.create(
            shop = 'slumber://pizzas/slumber_examples/Shop/data/1/')
        self.assertEqual(order.shop._url,
            'http://localhost:8000/slumber/pizzas/slumber_examples/Shop/data/1/')
        query = Order.objects.filter(shop=order.shop._url)
        self.assertEqual(query.count(), 1, [o.shop._url for o in list(Order.objects.all())])
