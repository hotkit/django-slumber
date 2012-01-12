from mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from slumber import client
from slumber._caches import CLIENT_INSTANCE_CACHE
from slumber.connector import Client, DictObject
from slumber_examples.models import Pizza, PizzaPrice, PizzaSizePrice


class TestDirectoryURLs(TestCase):
    def test_get_default_url_with_made_client(self):
        client = Client()
        self.assertEqual('http://localhost:8000/slumber/', client._directory)

    def test_get_default_url_with_default_client(self):
        self.assertEqual('http://localhost:8000/slumber/', client._directory)

    def test_get_default_url_with_services(self):
        with patch('slumber.server._get_slumber_directory', lambda: {
                'pizzas': 'http://localhost:8001/slumber/pizzas/',
                'takeaway': 'http://localhost:8002/slumber/'}):
            client = Client()
        self.assertIsNone(client._directory)


class TestLoads(TestCase):

    def test_applications_local(self):
        client = Client('http://localhost:8000/slumber')
        self.assertTrue(hasattr(client, 'slumber_examples'))

    def test_applications_remote(self):
        def request(k, u):
            self.assertEquals(u, 'http://slumber.example.com/')
            return DictObject(status=200), '''{"apps":{}}'''
        with patch('slumber.connector.ua.Http.request', self.fail):
            client = Client('http://slumber.example.com/')
        with patch('slumber.connector.ua.Http.request', request):
            try:
                client.no_module
                self.fail("This should have given an attribute error")
            except AttributeError:
                pass

    def test_applications_with_dots_in_name(self):
        client = Client()
        self.assertTrue(hasattr(client, 'django'), client.__dict__.keys())
        self.assertTrue(hasattr(client.django, 'contrib'), client.django.__dict__.keys())
        self.assertTrue(hasattr(client.django.contrib, 'sites'),
            (type(client.django.contrib), client.django.contrib.__dict__.keys()))
        try:
            client.django.NotAModelOrApp
            self.fail("This should have given an attribute error")
        except AttributeError:
            pass

    def test_new_client_gives_AttributeError_on_invalid_model(self):
        client = Client()
        try:
            client.django.contrib.auth.NotAModelOrApp
            self.fail("This should have given an attribute error")
        except AttributeError:
            pass

    def test_module_attributes(self):
        self.assertTrue(client.slumber_examples.Pizza.module, 'slumber_examples')
        self.assertTrue(client.slumber_examples.Pizza.name, 'Pizza')
        try:
            client.slumber_examples.Pizza.not_a_module_attr
            self.fail("This should have thrown an attribute error")
        except AttributeError:
            pass


class TestAuth(TestCase):
    def setUp(self):
        self.u = User(username='user')
        self.u.save()

    def test_has_attributes(self):
        user = client.django.contrib.auth.User.get(pk=self.u.pk)
        for attr in ['is_active', 'is_staff', 'date_joined', 'is_superuser',
                'first_name', 'last_name', 'email', 'username']:
            self.assertTrue(hasattr(user, attr), user.__dict__.keys())


class TestsWithPizza(TestCase):
    def setUp(self):
        self.s = Pizza(name='S1', for_sale=True)
        self.s.save()
        self.pizza = client.slumber_examples.Pizza.get(pk=self.s.pk)


    def test_instance_type(self):
        self.assertEqual(self.s.pk, self.pizza.id)
        self.assertEqual(type(self.pizza).__name__, 'slumber_examples.Pizza')
        pizza_type = str(type(self.pizza))
        self.assertTrue(pizza_type.endswith("slumber_examples.Pizza'>"),
            pizza_type)


    def test_cache_ttl(self):
        self.assertEqual(self.pizza._CACHE_TTL, 0)


    def test_instance_data(self):
        self.assertEqual('S1', self.pizza.name)
        prices = self.pizza.prices
        self.assertEqual(len(prices), 0)
        self.assertTrue(self.pizza.exclusive_to is None, self.pizza.exclusive_to)
        try:
            self.pizza.not_a_field
            self.fail("This should have thrown an AttributeError")
        except AttributeError:
            pass


    def test_instance_data_with_data_array(self):
        for p in range(15):
            PizzaPrice(pizza=self.s, date='2011-04-%s' % (p+1)).save()
        self.assertEqual('S1', self.pizza.name)
        prices = self.pizza.prices
        self.assertEquals(len(prices), 15)
        first_price = prices[0]
        self.assertEquals(unicode(first_price), "PizzaPrice object")
        self.assertEquals(first_price.pizza.for_sale, True)
        first_price_type = str(type(first_price))
        self.assertTrue(first_price_type.endswith("slumber_examples.PizzaPrice'>"),
            first_price_type)


    def test_instance_data_with_nested_data_array(self):
        p = PizzaPrice(pizza=self.s, date='2010-06-20')
        p.save()
        PizzaSizePrice(price=p, size='s', amount='13.95').save()
        PizzaSizePrice(price=p, size='m', amount='15.95').save()
        PizzaSizePrice(price=p, size='l', amount='19.95').save()
        self.assertEqual('S1', self.pizza.name)
        self.assertEqual(len(self.pizza.prices), 1)
        self.assertEqual(len(self.pizza.prices[0].amounts), 3)
        for a in self.pizza.prices[0].amounts:
            self.assertTrue(a.size in ['s', 'm', 'l'], a.size)


    def test_instance_no_pk(self):
        with self.assertRaises(AssertionError):
            pizza = client.slumber_examples.Pizza.get()


    def test_2nd_pizza_comes_from_cache(self):
        # Force a cache read
        self.assertEqual(unicode(self.pizza), u"S1")
        # Make a 2nd alias to the same object
        fail = lambda *a, **f: self.fail("_InstanceConnector.__init__ called again %s, %s" % (a, f))
        with patch('slumber.connector.api._InstanceConnector.__init__', fail):
            pizza2 = client.slumber_examples.Pizza.get(pk=self.s.pk)
            self.assertEqual(unicode(pizza2), u"S1")


    def test_pizza_not_found(self):
        with self.assertRaises(AssertionError):
            p2 = client.slumber_examples.Pizza.get(pk=2)
