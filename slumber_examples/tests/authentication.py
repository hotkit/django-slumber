from datetime import datetime
import logging
from mock import patch
from simplejson import loads

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import TestCase

from fost_authn.authentication import FostBackend

from slumber import client
from slumber._caches import PER_THREAD
from slumber.connector.authentication import Backend, \
    ImproperlyConfigured
from slumber.connector.ua import  _sign_request, get
from slumber.test import mock_client
from slumber_examples.models import Pizza, Profile
from slumber_examples.tests.configurations import ConfigureUser, \
    ConfigureAuthnBackend, PatchForAuthnService


class TestAuthnRequired(ConfigureUser, TestCase):
    def setUp(self):
        self.pizza = Pizza(name='Before change')
        self.pizza.save()
        super(TestAuthnRequired, self).setUp()

    def test_directory_works_when_not_authenticated(self):
        response = self.client.get('/slumber/')
        self.assertEqual(response.status_code, 200)

    def test_model_requires_authentication(self):
        response = self.client.get('/slumber/slumber_examples/Pizza/data/%s/' % self.pizza.pk)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get('WWW-Authenticate', None),
            'FOST Realm="Slumber"')

    def test_authenticated(self):
        response = self.signed_get(None,
            '/slumber/slumber_examples/Pizza/data/234234/')
        self.assertEqual(response.status_code, 404)
        json = loads(response.content)
        self.assertTrue(
            json["error"].startswith("Pizza matching query does not exist."),
            json["error"])

    def test_model_create_requires_permission(self):
        response = self.signed_post(self.user.username,
            '/slumber/slumber_examples/Pizza/create/',
            {'name': 'new test pizza'})
        self.assertEqual(response.status_code, 403)

    def test_model_create_checks_correct_permission(self):
        permission = Permission.objects.get(codename="add_pizza")
        self.user.user_permissions.add(permission)
        response = self.signed_post(None,
            '/slumber/slumber_examples/Pizza/create/',
            {'name': 'new test pizza'})
        self.assertEqual(response.status_code, 200, response.content)

    def test_model_update_requires_permission(self):
        response = self.signed_post(self.user.username,
            '/slumber/slumber_examples/Pizza/update/%s/' % self.pizza.pk,
            {'name': 'new test pizza'})
        self.assertEqual(response.status_code, 403)

    def test_model_update_checks_correct_permission(self):
        permission = Permission.objects.get(codename="change_pizza")
        self.user.user_permissions.add(permission)
        response = self.signed_post(self.user.username,
            '/slumber/slumber_examples/Pizza/update/%s/' % self.pizza.pk,
            {'name': 'new test pizza'})
        self.assertEqual(response.status_code, 200, response.content)

    def test_model_delete_requires_permission(self):
        response = self.signed_post(self.user.username,
            '/slumber/slumber_examples/Pizza/delete/%s/' % self.pizza.pk, {})
        self.assertEqual(response.status_code, 403)

    def test_model_delete_checks_correct_permission(self):
        permission = Permission.objects.get(codename="delete_pizza")
        self.user.user_permissions.add(permission)
        response = self.signed_post(self.user.username,
            '/slumber/slumber_examples/Pizza/delete/%s/' % self.pizza.pk, {})
        self.assertEqual(response.status_code, 200, response.content)


class TestAuthnForwarding(ConfigureUser, TestCase):
    def setUp(self):
        settings.MIDDLEWARE_CLASSES.append(
            'slumber.connector.middleware.ForwardAuthentication')
        super(TestAuthnForwarding, self).setUp()
    def tearDown(self):
        super(TestAuthnForwarding, self).tearDown()
        settings.MIDDLEWARE_CLASSES.remove(
            'slumber.connector.middleware.ForwardAuthentication')

    def test_signing_function_signs(self):
        headers = {}
        def check_request(request):
            for k, v in _sign_request('GET', '/', '', False).items():
                headers[k] = v
            return HttpResponse('ok', 'text/plain')
        with patch('slumber_examples.views._ok_text', check_request):
            self.client.get('/', REMOTE_ADDR='127.0.0.1')
        self.assertTrue(headers.has_key('Authorization'), headers)

    def test_username_with_colon(self):
        self.user.username = "my:name"
        self.user.save()
        headers = {}
        def check_request(request):
            for k, v in _sign_request('GET', '/', '', False).items():
                headers[k] = v
            return HttpResponse('ok', 'text/plain')
        with patch('slumber_examples.views._ok_text', check_request):
            self.signed_get(self.user.username)
        self.assertTrue(headers.has_key('Authorization'), headers)
        self.assertTrue(headers.has_key('X-FOST-User'), headers)
        self.assertEqual(headers['X-FOST-User'], self.user.username)

    def test_username_with_unicode(self):
        self.user.username = u"my\u2014name" # 0x2014 is mdash
        self.user.save()
        headers = {}
        def check_request(request):
            for k, v in _sign_request('GET', '/', '', False).items():
                headers[k] = v
            return HttpResponse('ok', 'text/plain')
        with patch('slumber_examples.views._ok_text', check_request):
            self.signed_get(self.user.username)
        self.assertTrue(headers.has_key('Authorization'), headers)
        self.assertTrue(headers.has_key('X-FOST-User'), headers)
        self.assertEqual(
            headers['X-FOST-User'].decode('utf-7'), self.user.username)

    def test_authentication_backend_accepts_signature(self):
        def check_request(request):
            class response:
                status = 200
                content = '''null'''
            def _request(_self, url, headers={}):
                backend = FostBackend()
                authz = headers['Authorization']
                key = authz[5:5+len(self.service.username)]
                signature = authz[6+len(self.service.username):]
                logging.info('Authorization %s %s', key, signature)
                request.META['HTTP_X_FOST_TIMESTAMP'] = headers[
                    'X-FOST-Timestamp']
                request.META['HTTP_X_FOST_HEADERS'] = headers[
                    'X-FOST-Headers']
                user = backend.authenticate(request=request,
                    key=key, hmac=signature)
                self.assertTrue(user)
                r = response()
                return r, r.content
            with patch('slumber.connector.ua.Http.request', _request):
                response, json = get('http://example.com/')
            return HttpResponse(response.content, 'text/plain')
        with patch('slumber_examples.views._ok_text', check_request):
            self.signed_get(self.user.username)


class TestBackend(PatchForAuthnService, TestCase):
    def setUp(self):
        super(TestBackend, self).setUp()
        self.backend = Backend()

    def test_remote_user(self):
        user = client.auth.django.contrib.auth.User.get(username='user')
        for attr in ['is_active', 'is_staff', 'date_joined', 'is_superuser',
                'first_name', 'last_name', 'email', 'username']:
            self.assertTrue(hasattr(user, attr), user.__dict__.keys())

    def test_remote_login(self):
        user = self.backend.authenticate(
            username=self.user.username, password='pass')
        self.assertTrue(user)
        self.assertEqual(user.username, self.user.username)

    def test_remote_login_with_unicode_username(self):
        # 2014 - mdash, 203d - interrobang
        self.user.username = u'interesting\u2014user\u203d'
        self.user.save()
        user = self.backend.authenticate(
            username=self.user.username, password='pass')
        self.assertTrue(user)
        self.assertEqual(user.username, self.user.username)

    def test_remote_login_with_unicode_password(self):
        # 203d - interrobang
        self.user.set_password(u'newpass\u203d')
        self.user.save()
        user = self.backend.authenticate(
            username=self.user.username, password=u'newpass\u203d')
        self.assertTrue(user)
        self.assertEqual(user.username, self.user.username)

    def test_remote_login_with_wrong_password(self):
        user = self.backend.authenticate(username=self.user.username, password='xxxx')
        self.assertIsNone(user)

    def test_login_type_not_recognised(self):
        user = self.backend.authenticate(made_up=True)
        self.assertIsNone(user)

    def test_get_user(self):
        user = self.backend.get_user(self.user.username)
        self.assertEqual(user.username, self.user.username)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertEqual(user.username, user.remote_user.username)
        self.assertEqual(user.is_active, user.remote_user.is_active)
        self.assertEqual(user.is_staff, user.remote_user.is_staff)
        self.assertEqual(user.is_superuser, user.remote_user.is_superuser)

    def test_get_user_with_id(self):
        user = self.backend.get_user(self.user.pk)
        self.assertTrue(user)

    def test_cache_ttl(self):
        user = self.backend.get_user(self.user.username)
        self.assertEqual(user.remote_user._CACHE_TTL, 120)

    def test_group_permissions(self):
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        perms = self.backend.get_group_permissions(user)
        self.assertEqual(perms, self.user.get_group_permissions())

    def test_all_permissions(self):
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        perms = self.backend.get_all_permissions(user)
        self.assertEqual(perms, self.user.get_all_permissions())

    def test_module_perms(self):
        user = self.backend.get_user(self.user.username)
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
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertTrue(self.backend.has_perm(user, 'slumber_examples.add_pizza'))

    def test_missing_permission(self):
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'slumber_examples.not-a-perm'))
        perm = Permission.objects.get(codename='not-a-perm',
            content_type__app_label='slumber_examples')
        self.assertEqual(perm.codename, 'not-a-perm')
        self.assertEqual(perm.name, perm.codename)
        self.assertEqual(perm.content_type.app_label, 'slumber_examples')
        self.assertEqual(perm.content_type.model, 'unknown')

    def test_permission_with_new_app(self):
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'not-an-app.not-a-perm'))
        perm = Permission.objects.get(codename='not-a-perm',
            content_type__app_label='not-an-app')
        self.assertEqual(perm.codename, 'not-a-perm')
        self.assertEqual(perm.name, perm.codename)
        self.assertEqual(perm.content_type.app_label, 'not-an-app')
        self.assertEqual(perm.content_type.model, 'unknown')

    def test_permission_with_invalid_name(self):
        user = self.backend.get_user(self.user.username)
        self.assertTrue(hasattr(user, 'remote_user'))
        self.assertFalse(self.backend.has_perm(user, 'not-a-perm'))
        self.assertFalse(self.backend.has_perm(user, 'not-an-app..not-a-perm'))

    def test_user_profile_when_no_profile(self):
        user = self.backend.get_user(self.user.username)
        with self.assertRaises(AssertionError):
            profile = user.get_profile()

    def test_user_profile_when_there_is_a_profile(self):
        profile = Profile(user=self.user)
        profile.save()
        user = self.backend.get_user(self.user.username)
        remote_profile = user.get_profile()
        self.assertEqual(remote_profile.id, profile.id)
        self.assertEqual(remote_profile.user.id, self.user.id)


class AuthenticationTests(ConfigureAuthnBackend, TestCase):
    def save_user(self, request):
        self.user = request.user
        return HttpResponse('ok')

    @mock_client(
        django__contrib__auth__User = []
    )
    def test_improperly_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            self.signed_get('testuser')

    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='testuser', is_active=True, is_staff=True,
                date_joined=datetime.now(), is_superuser=False,
                    first_name='Test', last_name='User',
                    email='test@example.com')],
    )
    def test_is_authenticated(self):
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.signed_get('testuser')
        self.assertTrue(self.user.is_authenticated())
        self.assertEqual(self.user.username, 'testuser')

    @mock_client(
        auth__django__contrib__auth__User = [
            dict(username='testuser', is_active=True, is_staff=False,
                date_joined=datetime.now(), is_superuser=False,
                    first_name='Test', last_name='User',
                    email='test@example.com')],
    )
    def test_created_user_sees_changes(self):
        self.signed_get('testuser')
        remote_user = client.auth.django.contrib.auth.User.get(
            username='testuser')
        remote_user.is_staff = True
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.signed_get('testuser')
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
            self.signed_get(admin.username)
        self.assertTrue(self.user.is_authenticated())
        self.assertEqual(admin, self.user)

    @mock_client(
        auth__django__contrib__auth__User = []
    )
    def test_remote_user_not_found(self):
        with patch('slumber_examples.views._ok_text', self.save_user):
            self.client.get('/', HTTP_X_FOST_USER='testuser')
        self.assertFalse(self.user.is_authenticated())
