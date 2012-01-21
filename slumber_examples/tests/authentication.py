from datetime import datetime
from mock import patch

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import TestCase

from slumber import client
from slumber.connector.authentication import Backend, \
    ImproperlyConfigured
from slumber.test import mock_client
from slumber_examples.models import Profile
from slumber_examples.tests.configurations import ConfigureAuthnBackend, \
    PatchForAuthnService


class TestBackend(PatchForAuthnService, TestCase):
    def setUp(self):
        super(TestBackend, self).setUp()
        self.backend = Backend()

    def test_remote_user(self):
        user = client.auth.django.contrib.auth.User.get(username='test')
        for attr in ['is_active', 'is_staff', 'date_joined', 'is_superuser',
                'first_name', 'last_name', 'email', 'username']:
            self.assertTrue(hasattr(user, attr), user.__dict__.keys())

    def test_delegated_login(self):
        user = self.backend.authenticate(x_fost_user=self.user.username)
        self.assertEqual(user.username, self.user.username)

    def test_remote_login(self):
        user = self.backend.authenticate(username=self.user.username, password='pass')
        self.assertEqual(user.username, self.user.username)

    def test_remote_login_with_wrong_password(self):
        user = self.backend.authenticate(username=self.user.username, password='xxxx')
        self.assertIsNone(user)

    def test_get_user(self):
        user = self.backend.get_user(self.user.username, 'username')
        self.assertEqual(user.username, self.user.username)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertEqual(user.username, user.remote_user.username)
        self.assertEqual(user.is_active, user.remote_user.is_active)
        self.assertEqual(user.is_staff, user.remote_user.is_staff)
        self.assertEqual(user.is_superuser, user.remote_user.is_superuser)

    def test_cache_ttl(self):
        user = self.backend.get_user(self.user.username, 'username')
        self.assertEqual(user.remote_user._CACHE_TTL, 120)

    def test_group_permissions(self):
        user = self.backend.get_user(self.user.username, 'username')
        self.assertTrue(hasattr(user, 'remote_user'))
        perms = self.backend.get_group_permissions(user)
        self.assertEqual(perms, self.user.get_group_permissions())

    def test_all_permissions(self):
        user = self.backend.get_user(self.user.username, 'username')
        self.assertTrue(hasattr(user, 'remote_user'))
        perms = self.backend.get_all_permissions(user)
        self.assertEqual(perms, self.user.get_all_permissions())

    def test_module_perms(self):
        user = self.backend.get_user(self.user.username, 'username')
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_module_perms(user, 'slumber_examples'))

    def test_existing_permission(self):
        self.assertTrue(bool(ContentType.objects.all().count()))
        content_type = ContentType.objects.get(
            app_label='slumber_examples', model='pizza')
        permission = Permission.objects.get(
            codename='add_pizza', content_type=content_type)
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'slumber_examples.add_pizza'))

    def test_existing_permission(self):
        self.assertTrue(bool(ContentType.objects.all().count()))
        content_type = ContentType.objects.get(
            app_label='slumber_examples', model='pizza')
        permission = Permission.objects.get(
            codename='add_pizza', content_type=content_type)
        self.user.user_permissions.add(permission)
        user = self.backend.get_user(self.user.username, 'username')
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertTrue(self.backend.has_perm(user, 'slumber_examples.add_pizza'))

    def test_missing_permission(self):
        user = self.backend.get_user(self.user.username, 'username')
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'slumber_examples.not-a-perm'))
        perm = Permission.objects.get(codename='not-a-perm',
            content_type__app_label='slumber_examples')
        self.assertEqual(perm.codename, 'not-a-perm')
        self.assertEqual(perm.name, perm.codename)
        self.assertEqual(perm.content_type.app_label, 'slumber_examples')
        self.assertEqual(perm.content_type.model, 'unknown')

    def test_permission_with_new_app(self):
        user = self.backend.get_user(self.user.pk)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'not-an-app.not-a-perm'))
        perm = Permission.objects.get(codename='not-a-perm',
            content_type__app_label='not-an-app')
        self.assertEqual(perm.codename, 'not-a-perm')
        self.assertEqual(perm.name, perm.codename)
        self.assertEqual(perm.content_type.app_label, 'not-an-app')
        self.assertEqual(perm.content_type.model, 'unknown')

    def test_permission_with_invalid_name(self):
        user = self.backend.get_user(self.user.pk)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'not-a-perm'))
        self.assertFalse(self.backend.has_perm(user, 'not-an-app..not-a-perm'))

    def test_user_profile_when_no_profile(self):
        user = self.backend.get_user(self.user.pk)
        with self.assertRaises(AssertionError):
            profile = user.get_profile()

    def test_user_profile_when_there_is_a_profile(self):
        profile = Profile(user=self.user)
        profile.save()
        user = self.backend.get_user(self.user.pk)
        remote_profile = user.get_profile()
        self.assertEqual(remote_profile.id, profile.id)
        self.assertEqual(remote_profile.user.id, self.user.id)


class AuthenticationTests(ConfigureAuthnBackend, TestCase):
    def save_user(self, request):
        self.user = request.user
        return HttpResponse('ok')

    @mock_client()
    def test_isnt_authenticated(self):
        with patch('slumber_examples.views._ok_text', self.save_user):
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
            dict(username='testuser', is_active=True, is_staff=True,
                date_joined=datetime.now(), is_superuser=False,
                    first_name='Test', last_name='User',
                    email='test@example.com')],
    )
    def test_is_authenticated(self):
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertTrue(self.user.is_authenticated())

    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='testuser', is_active=True, is_staff=False,
                date_joined=datetime.now(), is_superuser=False,
                    first_name='Test', last_name='User',
                    email='test@example.com')],
    )
    def test_created_user_sees_changes(self):
        self.client.get('/', HTTP_X_FOST_USER='testuser')
        remote_user = client.auth.django.contrib.auth.User.get(
            username='testuser')
        remote_user.is_staff = True
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertTrue(self.user.is_staff)

    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='admin', is_active=True, is_staff=True,
                date_joined=datetime.now(), is_superuser=False,
                    first_name='Test', last_name='User',
                    email='test@example.com')],
    )
    def test_admin_is_authenticated(self):
        admin = User(username='admin')
        admin.save()
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER=admin.username)
        self.assertTrue(self.user.is_authenticated())
        self.assertEqual(admin, self.user)

    @mock_client(
        auth__django__contrib__auth__User = []
    )
    def test_remote_user_not_found(self):
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertFalse(self.user.is_authenticated())
