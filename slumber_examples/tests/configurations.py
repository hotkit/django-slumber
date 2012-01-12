from mock import patch

from django.conf import settings
from django.contrib.auth.models import User

from slumber.connector import Client


class ConfigureAuthnBackend(object):
    def setUp(self):
        self.user = User(username='user', is_active=True, is_staff=True)
        self.user.set_password('pass')
        self.user.save()

        self.assertFalse(hasattr(settings, 'SLUMBER_DIRECTORY'))
        self.assertFalse(hasattr(settings, 'SLUMBER_SERVICE'))
        self.__backends = settings.AUTHENTICATION_BACKENDS
        settings.AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'slumber.connector.authentication.Backend',
        )
        settings.MIDDLEWARE_CLASSES.append(
            'slumber.connector.middleware.Authentication')
        super(ConfigureAuthnBackend, self).setUp()

    def tearDown(self):
        super(ConfigureAuthnBackend, self).tearDown()
        settings.AUTHENTICATION_BACKENDS = self.__backends
        settings.MIDDLEWARE_CLASSES.remove(
            'slumber.connector.middleware.Authentication')


class PatchForAuthnService(object):
    def setUp(self):
        user = User(username='test', is_active=True, is_staff=True,
            is_superuser=False)
        user.set_password('pass')
        user.save()
        self.user = User.objects.get(username=user.username)

        self.assertFalse(hasattr(settings, 'SLUMBER_DIRECTORY'))
        self.assertFalse(hasattr(settings, 'SLUMBER_SERVICE'))
        service = lambda: 'auth'
        directory = lambda: {
            'auth': 'http://localhost:8000/slumber/auth/',
        }
        self.__patchers = [
            patch('slumber.server._get_slumber_service', service),
            patch('slumber.server._get_slumber_directory', directory),
        ]
        [p.start() for p in self.__patchers]
        client_patch = patch('slumber._client', Client())
        client_patch.start()
        self.__patchers.append(client_patch)
        super(PatchForAuthnService, self).setUp()
    def tearDown(self):
        super(PatchForAuthnService, self).tearDown()
        [p.stop() for p in self.__patchers]

