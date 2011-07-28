from decimal import Decimal

from unittest2 import TestCase

from slumber import client
from slumber.test import mock_client


class TestSlumberMock(TestCase):
    margarita = dict(pk=1, name='Margarita', for_sale=True)

    @mock_client(app__contrib__auth__Model=[], app__Pizza=[])
    def test_basic_app_data(self):
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
        p1 = client.slumber.Pizza.get(pk=1)
        self.assertEquals(p1.pk, 1)
        self.assertEquals(getattr(p1, 'name', None), 'Margarita', p1.__dict__)
        p2 = client.slumber.Pizza.get(pk=2)
        self.assertEquals(p2.pk, 2)

        pp1 = client.slumber.PizzaPrice.get(pk=1)
        self.assertEquals(pp1.pk, 1)
        self.assertEquals(pp1.pizza.name, 'Margarita')

