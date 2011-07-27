from decimal import Decimal

from unittest2 import TestCase

from slumber import client
from slumber.test import mock_client


class TestSlumberMock(TestCase):
    margarita = dict(pk=1, name='Margarita', for_sale=True)

    @mock_client(django__contrib__auth__User=[], slumber__Pizza=[])
    def test_basic_app_data(self):
        self.assertTrue(hasattr(client, 'django'))
        self.assertTrue(hasattr(client, 'slumber'))

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
        self.assertTrue(client.slumber.Pizza.get(pk=1))
