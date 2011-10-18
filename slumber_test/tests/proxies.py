from unittest2 import TestCase

from slumber import client
from slumber.connector.proxies import UserProxy
from slumber.test import mock_client


class UserProxyTests(TestCase):
    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='test')
        ]
    )
    def test_user_proxy_is_used(self):
        user = client.auth.django.contrib.auth.User.get(username='test')
        self.assertIn(UserProxy, user.__bases__)
