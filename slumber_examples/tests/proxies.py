from django.test import TestCase

from slumber import client
from slumber.connector import Client
from slumber.connector.proxies import UserInstanceProxy
from slumber_examples.models import Pizza
from slumber_examples.tests.configurations import PatchForAuthnService


class UserProxyTests(PatchForAuthnService, TestCase):
    def setUp(self):
        super(UserProxyTests, self).setUp()
        self.proxy_user = client.auth.django.contrib.auth.User.get(username='user')

    def test_user_proxy_is_used(self):
        self.assertIn(UserInstanceProxy, type(self.proxy_user).__mro__)

    def test_has_perm(self):
        self.assertFalse(self.proxy_user.has_perm('slumber_examples.not-a-permission'))

    def test_user_has_module_permission(self):
        self.assertFalse(self.proxy_user.has_module_perms('slumber_examples'))

    def test_user_get_group_permissions(self):
        perms = self.proxy_user.get_group_permissions()
        self.assertEqual(self.user.get_group_permissions(), perms)

    def test_user_get_all_permissions(self):
        perms = self.proxy_user.get_all_permissions()
        self.assertEqual(self.user.get_all_permissions(), perms)


class ProxyConfigurationTests(TestCase):
    def test_shop_has_model_proxy(self):
        self.assertTrue(
            client.slumber_examples.Shop.has_shop_proxy())

    def test_pizza_has_instance_proxy(self):
        lpizza = Pizza(name='Test pizza')
        lpizza.save()
        rpizza = client.slumber_examples.Pizza.get(
            pk=lpizza.pk)
        self.assertTrue(rpizza.has_pizza_proxy())
