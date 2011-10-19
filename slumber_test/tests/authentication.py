from mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase

from slumber.connector import Client
from slumber.connector.authentication import Backend, \
    ImproperlyConfigured
from slumber.test import mock_client
from slumber_test.tests.configurations import ConfigureAuthnBackend, \
    PatchForAuthnService


class TestBackend(PatchForAuthnService, TestCase):
    def setUp(self):
        super(TestBackend, self).setUp()
        self.backend = Backend()

    def test_get_user(self):
        with patch('slumber._client', self.slumber_client): # We have to patch this late
            user = self.backend.get_user(self.user.username)
            self.assertEqual(user.username, self.user.username)
            self.assertTrue(user.is_active)
            self.assertTrue(user.is_staff)
            self.assertTrue(hasattr(user, 'remote_user'))
            self.assertEqual(user.username, user.remote_user.username)

    def test_group_permissions(self):
        with patch('slumber._client', self.slumber_client): # We have to patch this late
            user = self.backend.get_user(self.user.username)
            self.assertTrue(hasattr(user, 'remote_user'))
            perms = self.backend.get_group_permissions(user)


class AuthenticationTests(ConfigureAuthnBackend, TestCase):
    def save_user(self, request):
        self.user = request.user
        return HttpResponse('ok')

    @mock_client()
    def test_isnt_authenticated(self):
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/')
        self.assertFalse(self.user.is_authenticated())

    @mock_client(
        django__contrib__auth__User = [],
    )
    def test_improperly_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get('/', HTTP_X_FOST_USER='testuser')

    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='testuser', is_active=True, is_staff=True)],
    )
    def test_is_authenticated(self):
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertTrue(self.user.is_authenticated())

    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='admin', is_active=True, is_staff=True)],
    )
    def test_admin_is_authenticated(self):
        admin = User(username='admin')
        admin.save()
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER=admin.username)
        self.assertTrue(self.user.is_authenticated())
        self.assertEqual(admin, self.user)

    @mock_client(
        auth__django__contrib__auth__User = []
    )
    def test_remote_user_not_found(self):
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertFalse(self.user.is_authenticated())

