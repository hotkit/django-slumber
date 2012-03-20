from simplejson import loads

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
        response = self.client.get('/slumber/slumber_examples/Pizza/order/1/')
        self.assertEquals(response.status_code, 200, response.content)
        json = loads(response.content)
        self.assertEquals(json, dict(
                _meta = dict(status=200, message="OK"),
                form = dict(quantity='integer'),
            ))

    def test_order_post(self):
        pizza = self.cnx.slumber_examples.Pizza.get(id=self.pizza.id)
        response = self.client.post('/slumber/slumber_examples/Pizza/order/1/',
            dict(quantity=3))
        self.assertEquals(response.status_code, 501, response.content)
