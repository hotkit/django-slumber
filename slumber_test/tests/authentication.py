from mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase


class ConfigureAuthn(object):
    def setUp(self):
        self.__backends = settings.AUTHENTICATION_BACKENDS
        settings.AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'slumber.connector.authentication.Backend',
        )
        settings.MIDDLEWARE_CLASSES.append(
            'slumber.connector.middleware.Authentication')
        super(ConfigureAuthn, self).setUp()

    def tearDown(self):
        super(ConfigureAuthn, self).tearDown()
        settings.AUTHENTICATION_BACKENDS = self.__backends
        settings.MIDDLEWARE_CLASSES.remove(
            'slumber.connector.middleware.Authentication')


class AuthenticationTests(ConfigureAuthn, TestCase):
    def save_user(self, request):
        self.user = request.user
        return HttpResponse('ok')

    def test_isnt_authenticated(self):
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/')
        self.assertFalse(self.user.is_authenticated())

    def test_is_authenticated(self):
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertTrue(self.user.is_authenticated())

    def test_admin_is_authenticated(self):
        admin = User(username='admin')
        admin.save()
        with patch('slumber_test.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER=admin.username)
        self.assertTrue(self.user.is_authenticated())
        self.assertEqual(admin, self.user)
