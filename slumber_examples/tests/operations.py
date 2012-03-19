from django.test import TestCase

from slumber import Client

from slumber_examples.models import Pizza


class OrderTests(TestCase):
    def setUp(self):
        self.pizza = Pizza(name='S1', for_sale=True)
        self.pizza.save()
        self.cnx = Client()

    def test_order_get(self):
        pizza = self.cnx.slumber_examples.Pizza.get(id=self.pizza.id)
        self.assertEquals(pizza._operations['order'],
            'http://localhost:8000/slumber/slumber_examples/Pizza/order/1/')
