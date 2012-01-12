from decimal import Decimal

import django.test
import mock
import unittest2

from django.http import HttpResponse

from slumber import client
from slumber.test import mock_client


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
           margarita ,
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
        self.assertEquals(type(p1).__name__, "Pizza")

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
