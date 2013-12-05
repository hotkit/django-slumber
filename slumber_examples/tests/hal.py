from django.test import TestCase

from slumber.connector.ua import get

from slumber_examples.models import Shop
from slumber_examples.tests.configurations import ConfigureUser


class TestInstanceList(ConfigureUser, TestCase):
    def test_empty_hal_version(self):
        response, json = get('/slumber/shops/mount2/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.has_key('instances'))

        self.assertTrue(json['instances'].has_key('_links'))
        links = json['instances']['_links']
        self.assertEqual(links['self']['href'], '/slumber/shops/mount2/')
        self.assertEqual(links['model']['href'], '/slumber/slumber_examples/Shop/')

    def test_five_shops(self):
        for s in xrange(1, 6):
            Shop.objects.create(name="Shop %d" % s, slug="shop%d" % s)
        response, json = get('/slumber/shops/mount2/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.has_key('instances'))

        self.assertTrue(json['instances'].has_key('_links'))
        links = json['instances']['_links']
        self.assertEqual(links['self']['href'], '/slumber/shops/mount2/')
        self.assertEqual(links['model']['href'], '/slumber/slumber_examples/Shop/')

        self.assertTrue(json['instances'].has_key('_embedded'))
        self.assertTrue(json['instances']['_embedded'].has_key('page'))
        page = json['instances']['_embedded']['page']

        self.assertEqual(len(page), 5)
        self.assertEqual(page[0], dict(
            _links={'self': dict(href='/slumber/pizzas/shop/5/')},
            display="Shop 5"))

