from mock import patch

from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase


class ConfigureAuthn(object):
    def setUp(self):
        settings.MIDDLEWARE_CLASSES.append(
            'slumber.connector.middleware.Authentication')
        super(ConfigureAuthn, self).setUp()

    def tearDown(self):
        super(ConfigureAuthn, self).tearDown()
        settings.MIDDLEWARE_CLASSES.remove(
            'slumber.connector.middleware.Authentication')


class AuthenticationTests(ConfigureAuthn, TestCase):
    def setUp(self):
        self.called = []
        super(AuthenticationTests, self).setUp()

    def check_authentication(self, request):
            self.called.append(request.user.is_authenticated())
            return HttpResponse('ok')

    def test_not_authenticated(self):
        with patch('slumber_test.views.ok_text', self.check_authentication):
            self.client.get('/')
        self.assertTrue(bool(len(self.called)))
        self.assertEqual(self.called, [False])

    def test_is_authenticated(self):
        pass
