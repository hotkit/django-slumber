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

