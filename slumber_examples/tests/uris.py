from django.test import TestCase

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


class TestShopURIs(TestCase):
    def test_model_has_slumber_model(self):
        self.assertEqual(Shop.slumber_model,
            DJANGO_MODEL_TO_SLUMBER_MODEL[Shop])

    def test_instance_data_uri(self):
        shop = Shop.objects.create(name="Test Cafe")
        self.assertEqual(type(shop).slumber_model.operations['data'](shop.pk),
            '/slumber/pizzas/shop/1/')

    def test_spaces_in_url_fragment(self):
        self.assertEqual(Shop.slumber_model.operations['shops1']('with space'),
            r'/slumber/shops/mount1/with%20space/')
