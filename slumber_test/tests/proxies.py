from django.test import TestCase

from slumber.connector.proxies import UserProxy
from slumber_test.tests.configurations import PatchForAuthnService


class UserProxyTests(PatchForAuthnService, TestCase):
    def test_user_proxy_is_used(self):
        user = self.slumber_client.auth.django.contrib.auth.User.get(username='test')
        self.assertIn(UserProxy, type(user).__mro__)

    def test_has_perm(self):
        user = self.slumber_client.auth.django.contrib.auth.User.get(username='test')
        self.assertFalse(user.has_perm('slumber_test.not-a-permission'))

    def test_user_has_module_permission(self):
        user = self.slumber_client.auth.django.contrib.auth.User.get(username='test')
        self.assertFalse(user.has_module_perms('slumber_test'))

    def test_user_get_group_permissions(self):
        user = self.slumber_client.auth.django.contrib.auth.User.get(username='test')
        perms = user.get_group_permissions()
        self.assertEqual(self.user.get_group_permissions(), perms)

    def test_user_get_all_permissions(self):
        user = self.slumber_client.auth.django.contrib.auth.User.get(username='test')
        perms = user.get_all_permissions()
        self.assertEqual(self.user.get_all_permissions(), perms)

