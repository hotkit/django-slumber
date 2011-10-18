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
    def test_no_middleware_error(self):
        called = []
        def view(request):
            called.append(True)
            return HttpResponse('ok')
        with patch('slumber_test.views.ok_text', view):
            self.client.get('/')
        self.assertEqual(called, [True])
