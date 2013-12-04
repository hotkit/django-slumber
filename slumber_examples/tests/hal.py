from django.test import TestCase

from slumber.connector.ua import get

from slumber_examples.tests.configurations import ConfigureUser


class TestInstanceList(ConfigureUser, TestCase):
    def test_hal_version(self):
        response, json = get('/slumber/shops/mount2/')
        self.assertEqual(response.status_code, 200)

