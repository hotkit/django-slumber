from django.test import TestCase


class ConfigureAuthn(object):
    def setUp(self):
        super(ConfigureAuthn, self).setUp()

    def tearDown(self):
        super(ConfigureAuthn, self).tearDown()


class AuthenticationTests(ConfigureAuthn, TestCase):
    def test_middleware(self):
        pass
