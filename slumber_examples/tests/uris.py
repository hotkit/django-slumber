from django.test import TestCase

from slumber import data_link
from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL

from slumber_examples.models import Pizza, Shop


class TestPizzaURIs(TestCase):
    def test_model_has_slumber_model(self):
        self.assertEqual(Pizza.slumber_model,
            DJANGO_MODEL_TO_SLUMBER_MODEL[Pizza])

    def test_instance_data_url(self):
        pizza = Pizza.objects.create(name="Test pizza")
        self.assertEqual(type(pizza).slumber_model.operations['data'](pizza.pk),
            '/slumber/slumber_examples/Pizza/data/%s/' % pizza.pk)

    def test_data_link(self):
        pizza = Pizza.objects.create(name="Test pizza")
        self.assertEqual(data_link(pizza),
            '/slumber/slumber_examples/Pizza/data/%s/' % pizza.pk)

    def test_instance_data_url_when_passed_instance(self):
        pizza = Pizza.objects.create(name="Test pizza")
        self.assertEqual(type(pizza).slumber_model.operations['data'](pizza),
            '/slumber/slumber_examples/Pizza/data/%s/' % pizza.pk)


class TestShopURIs(TestCase):
    def test_model_has_slumber_model(self):
        self.assertEqual(Shop.slumber_model,
            DJANGO_MODEL_TO_SLUMBER_MODEL[Shop])

    def test_instance_data_uri(self):
        shop = Shop.objects.create(name="Test Cafe")
        self.assertEqual(type(shop).slumber_model.operations['data'](shop.pk),
            '/slumber/pizzas/shop/%s/' % shop.pk)

    def test_data_link(self):
        shop = Shop.objects.create(name="Test Cafe")
        self.assertEqual(data_link(shop), '/slumber/pizzas/shop/%s/' % shop.pk)

    def test_spaces_in_url_fragment(self):
        self.assertEqual(Shop.slumber_model.operations['shops1']('with space'),
            r'/slumber/shops/mount1/with%20space/')

    def test_query_string(self):
        self.assertEqual(Shop.slumber_model.operations['shops1'](key='v1'),
            r'/slumber/shops/mount1/?key=v1')

    def test_argument_which_re_roots(self):
        self.assertEqual(
            Shop.slumber_model.operations['shops1']('/shops/mount1'),
            r'/slumber/shops/mount1/')

    def test_argument_which_re_roots_all_the_way(self):
        self.assertEqual(
            Shop.slumber_model.operations['shops1']('/slumber/shops/mount1'),
            r'/slumber/shops/mount1/')
