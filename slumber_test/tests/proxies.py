from mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from slumber.connector import Client
from slumber.connector.proxies import UserProxy
from slumber.test import mock_client


class ConfigureSlumber(object):
    def setUp(self):
        self.user = User(username='test')
        self.user.save()

        self.assertFalse(hasattr(settings, 'SLUMBER_DIRECTORY'))
        self.assertFalse(hasattr(settings, 'SLUMBER_SERVICE'))
        service = lambda: 'auth'
        directory = lambda: {
            'auth': 'http://localhost:8000/slumber/auth/',
        }
        self.__patchers = [
            patch('slumber.server.views.get_slumber_service', service),
            patch('slumber.server.get_slumber_service', service),
            patch('slumber.server.get_slumber_directory', directory),
        ]
        [p.start() for p in self.__patchers]
        self.client = Client()
    def tearDown(self):
        [p.stop() for p in self.__patchers]


class UserProxyTests(ConfigureSlumber, TestCase):
    def test_user_proxy_is_used(self):
        user = self.client.auth.django.contrib.auth.User.get(username='test')
        self.assertIn(UserProxy, type(user).__mro__)

    def test_user_get_group_permissions(self):
        user = self.client.auth.django.contrib.auth.User.get(username='test')
        perms = user.get_group_permissions()
        self.assertEqual(self.user.get_group_permissions(), perms)

