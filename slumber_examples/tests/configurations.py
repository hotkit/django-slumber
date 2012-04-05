from mock import patch

from django.conf import settings
from django.contrib.auth.models import User

from slumber.connector import Client
from slumber.connector.ua import _calculate_signature


class ConfigureUser(object):
    def setUp(self):
        self.user = User(username='user', is_active=True, is_staff=True,
            is_superuser=False)
        self.user.set_password('pass')
        self.user.save()
        self.service = User(username='service', is_active=True, is_staff=True,
            is_superuser=True, password=settings.SECRET_KEY)
        self.service.save()
        self.__patchers = [
            patch('slumber.connector._get_slumber_authn_name', lambda: 'service'),
        ]
        [p.start() for p in self.__patchers]
        super(ConfigureUser, self).setUp()
    def tearDown(self):
        super(ConfigureUser, self).tearDown()
        [p.stop() for p in self.__patchers]

    def signed_get(self,  username, url='/'):
        headers = _calculate_signature('service', 'GET', url, '', username, True)
        return self.client.get(url, **headers)

    def signed_post(self, username, url, data):
        headers = _calculate_signature('service', 'POST', url, data, username, True)
        return self.client.post(url, data, **headers)


class ConfigureAuthnBackend(ConfigureUser):
    def setUp(self):
        self.assertFalse(hasattr(settings, 'SLUMBER_DIRECTORY'))
        self.assertFalse(hasattr(settings, 'SLUMBER_SERVICE'))
        self.__backends = settings.AUTHENTICATION_BACKENDS
        settings.AUTHENTICATION_BACKENDS = [
            'slumber.connector.authentication.Backend',
        ]
        super(ConfigureAuthnBackend, self).setUp()

    def tearDown(self):
        super(ConfigureAuthnBackend, self).tearDown()
        settings.AUTHENTICATION_BACKENDS = self.__backends


class PatchForAuthnService(ConfigureUser):
    def setUp(self):
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
        self.user = User.objects.get(username=self.user.username)
    def tearDown(self):
        super(PatchForAuthnService, self).tearDown()
        [p.stop() for p in self.__patchers]

