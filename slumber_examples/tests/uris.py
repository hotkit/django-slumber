from django.test import TestCase

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL

from slumber_examples.models import Pizza, Shop


class TestPizzaURIs(TestCase):
    def test_model_has_slumber_model(self):
        self.assertEqual(Pizza.slumber_model,
            DJANGO_MODEL_TO_SLUMBER_MODEL[Pizza])


class TestShopURIs(TestCase):
    def test_model_has_slumber_model(self):
        self.assertEqual(Shop.slumber_model,
            DJANGO_MODEL_TO_SLUMBER_MODEL[Shop])

