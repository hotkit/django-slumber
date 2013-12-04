from mock import patch
from simplejson import loads

from django.test import TestCase

from slumber import Client
from slumber.connector.ua import post, get

from slumber_examples.models import Pizza, PizzaCrust, Shop
from slumber_examples.tests.configurations import ConfigureUser


class CreateTests(ConfigureUser, TestCase):
    def test_create_pizza(self):
        response, json = post('/slumber/slumber_examples/Pizza/create/', {
            'id': 1, 'name': 'Test P', 'for_sale': True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.has_key('pk'), json)
        self.assertEqual(json['pk'], 1, json)
        self.assertTrue(json.has_key('created'), json)
        self.assertTrue(json['created'], json)
        self.assertEqual(Pizza.objects.all().count(), 1)

    def test_create_pizza_twice(self):
        response1, json1 = post('/slumber/slumber_examples/Pizza/create/', {
                'id': 1, 'name': 'Test P', 'for_sale': True})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(json1['created'], json1)

        response2, json2 = post('/slumber/slumber_examples/Pizza/create/', {
                'id': 1, 'name': 'Test P', 'for_sale': True})
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(json2['created'], json2)
        self.assertEqual(Pizza.objects.all().count(), 1)

    def test_create_pizza_crust(self):
        response1, json1 = post('/slumber/slumber_examples/PizzaCrust/create/', {
                'code': 'org', 'full_name': 'original crust'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(json1['created'], json1)
        self.assertEqual(PizzaCrust.objects.all().count(), 1)

    def test_update_pizza(self):
        self.cnx = Client()
        p_id, p_sale = 1 , False
        response1, json1 = post('/slumber/slumber_examples/Pizza/create/',{
                'id':p_id, 'name':'Test P', 'for_sale': True})
        self.assertEqual(response1.status_code, 200)
        pizza = self.cnx.slumber_examples.Pizza.get(pk = p_id)
        self.cnx.slumber_examples.Pizza.update(pizza, for_sale = p_sale)
        pizza = self.cnx.slumber_examples.Pizza.get(pk = p_id)
        self.assertEqual(pizza.for_sale, p_sale)


class OrderTests(ConfigureUser, TestCase):
    def setUp(self):
        super(OrderTests, self).setUp()
        self.pizza = Pizza(name='S1', for_sale=True)
        self.pizza.save()
        self.cnx = Client()

    def test_order_get(self):
        with patch('slumber.connector._get_slumber_authn_name', lambda: 'service'):
            pizza = self.cnx.slumber_examples.Pizza.get(id=self.pizza.id)
            self.assertEquals(pizza._operations['order'],
                'http://localhost:8000/slumber/slumber_examples/Pizza/order/1/')
            # Do an unsigned GET so there will be no user logged in
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

    def test_order_create_with_pk(self):
        pizza2 = self.cnx.slumber_examples.Pizza.create(id=2, name='S2', for_sale=True)
        pizza3 = Pizza.objects.create(name='S3', for_sale=True)
        self.assertEqual(Pizza.objects.count(), 3)


class ShopListTests(TestCase):
    def setUp(self):
        super(ShopListTests, self).setUp()
        self.cnx = Client()

    def test_mount_point(self):
        response, json = get('/slumber/shops/mount1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json, dict(_meta={'message': 'OK', 'status': 200},
            shops=[{
                'name': 'Hard Coded Pizza Parlour'
            }]))

    def test_operation_model_uri(self):
        self.assertTrue(
            self.cnx.slumber_examples.Shop._operations.has_key('shops1'),
            self.cnx.slumber_examples.Shop._operations.keys())
        self.assertEqual(
            self.cnx.slumber_examples.Shop._operations["shops1"],
            'http://localhost:8000/slumber/shops/mount1/')


class ShopInstanceTests(ConfigureUser, TestCase):
    def test_mount_point(self):
        shop = Shop.objects.create(name='Test One')
        with patch('slumber.connector._get_slumber_authn_name', lambda: 'service'):
            response, json = get('/slumber/pizzas/shop/%s/' % shop.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json['operations'].has_key('data'), json)
        self.assertEqual(json['operations']['data'],
            '/slumber/pizzas/shop/%s/' % shop.pk)


