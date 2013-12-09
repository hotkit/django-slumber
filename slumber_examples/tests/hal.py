from __future__ import absolute_import

from django.test import TestCase
from xml.dom.minidom import parseString

from slumber.connector.ua import get

from slumber_examples.models import Shop
from slumber_examples.tests.configurations import ConfigureUser


class TestInstanceList(ConfigureUser, TestCase):
    def test_empty_hal_version(self):
        response, json = get('/slumber/shops/mount2/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.has_key('instances'))

        self.assertTrue(json.has_key('_links'))
        links = json['_links']
        self.assertEqual(links['self']['href'], '/slumber/shops/mount2/')
        self.assertEqual(links['model']['href'], '/slumber/slumber_examples/Shop/')

    def test_five_shops(self):
        for s in xrange(1, 6):
            Shop.objects.create(name="Shop %d" % s, slug="shop%d" % s)
        response, json = get('/slumber/shops/mount2/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.has_key('instances'))

        self.assertTrue(json.has_key('_links'))
        links = json['_links']
        self.assertEqual(links['self']['href'], '/slumber/shops/mount2/')
        self.assertEqual(links['model']['href'], '/slumber/slumber_examples/Shop/')
        self.assertFalse(links.has_key('next'), links)

        self.assertTrue(json.has_key('_embedded'))
        self.assertTrue(json['_embedded'].has_key('page'))
        page = json['_embedded']['page']

        self.assertEqual(len(page), 5)
        self.assertEqual(page[0], dict(
            _links={'self': dict(href='/slumber/pizzas/shop/5/')},
            display="Shop 5"))

    def test_ten_shops(self):
        for s in xrange(1, 11):
            Shop.objects.create(name="Shop %d" % s, slug="shop%2d" % s)
        response, json = get('/slumber/shops/mount2/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.has_key('instances'))

        self.assertTrue(json.has_key('_links'))
        links = json['_links']
        self.assertEqual(links['self']['href'], '/slumber/shops/mount2/')
        self.assertEqual(links['model']['href'], '/slumber/slumber_examples/Shop/')
        self.assertFalse(links.has_key('next'), links)

        self.assertTrue(json.has_key('_embedded'))
        self.assertTrue(json['_embedded'].has_key('page'))
        page = json['_embedded']['page']

        self.assertEqual(len(page), 10)
        self.assertEqual(page[0], dict(
            _links={'self': dict(href='/slumber/pizzas/shop/10/')},
            display="Shop 10"))

    def test_fifteen_shops(self):
        for s in xrange(1, 16):
            Shop.objects.create(name="Shop %d" % s, slug="shop%2d" % s)
        response, json = get('/slumber/shops/mount2/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.has_key('instances'))

        self.assertTrue(json.has_key('_links'))
        links = json['_links']
        self.assertEqual(links['self']['href'], '/slumber/shops/mount2/')
        self.assertEqual(links['model']['href'], '/slumber/slumber_examples/Shop/')
        self.assertTrue(links.has_key('next'), links)

        self.assertTrue(json.has_key('_embedded'))
        self.assertTrue(json['_embedded'].has_key('page'))
        page = json['_embedded']['page']

        self.assertEqual(len(page), 10)
        self.assertEqual(page[0], dict(
            _links={'self': dict(href='/slumber/pizzas/shop/15/')},
            display="Shop 15"))

        self.assertEqual(links['next']['href'],
            '/slumber/shops/mount2/?lpk=6')

    def test_fifteen_shops_page_2(self):
        for s in xrange(1, 16):
            Shop.objects.create(name="Shop %d" % s, slug="shop%2d" % s)
        response, json = get('/slumber/shops/mount2/?lpk=6')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.has_key('instances'))

        self.assertTrue(json.has_key('_links'))
        links = json['_links']
        self.assertFalse(links.has_key('next'), links)

        self.assertTrue(json.has_key('_embedded'))
        self.assertTrue(json['_embedded'].has_key('page'))
        page = json['_embedded']['page']

        self.assertEqual(len(page), 5)
        self.assertEqual(page[0], dict(
            _links={'self': dict(href='/slumber/pizzas/shop/5/')},
            display="Shop 5"))

    def test_xml(self):
        response, _ = get('/slumber/shops/mount2/?lpk=6',
            headers=dict(Accept='application/xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')

        xml = parseString(response.content)
        self.assertEqual(xml.documentElement.tagName, 'instances')
