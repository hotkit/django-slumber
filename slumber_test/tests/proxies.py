from unittest2 import TestCase

from slumber import client
from slumber.connector.proxies import UserProxy
from slumber.test import mock_client


class UserProxyTests(TestCase):
    def test_user_proxy_is_used(self):
        user = client.auth.django.contrib.auth.User.get(username='test')
        self.assertIn(UserProxy, type(user).__mro__)
