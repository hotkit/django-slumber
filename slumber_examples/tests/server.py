from datetime import date
from simplejson import loads
from mock import patch, Mock

from django.test import TestCase

from slumber._caches import DJANGO_MODEL_TO_SLUMBER_MODEL
from slumber.server import get_slumber_services, get_slumber_local_url_prefix, \
    NoServiceSpecified, AbsoluteURIRequired, Forbidden
from slumber.server.http import view_handler, require_permissions
from slumber.server.meta import get_application

from slumber_examples.models import Pizza
from slumber_examples.tests import ConfigureUser


class TestJSON(TestCase):
    def test_unicode_attributes(self):
        d = date.today()
        class Request(object):
            META = {}
            class user(object):
                @classmethod
                def is_authenticated(cls):
                    return True
                username = 'testuser'
        @view_handler
        def view(request, response):
            response['u'] = d
        http_response = view(Request())
        content = loads(http_response.content)
        self.assertEquals(content, dict(
            u = str(d),
            _meta = dict(status = 200, message = "OK", username = "testuser")))


class InternalAPIs(TestCase):
    def test_get_application(self):
        app = get_application('slumber_examples')
        self.assertEqual(app.name, 'slumber_examples')
        self.assertEqual(app.path, 'slumber_examples')

    def test_slumber_services_none(self):
        directory = get_slumber_services()
        self.assertIsNone(directory)

    def test_slumber_services(self):
        with patch('slumber.server.get_slumber_directory', lambda: {
                'pizzas': '/slumber/pizzas/',
                'takeaway': 'http://localhost:8002:/slumber/'}):
            directory = get_slumber_services()
            self.assertIsNotNone(directory)

    def test_slumber_local_url(self):
        with patch('slumber.server.get_slumber_directory',
                lambda: 'http://example.com/somewhere/slumber/'):
            self.assertEqual(get_slumber_local_url_prefix(),
                'http://example.com/')

    def test_slumber_local_url_dev_server(self):
        with patch('slumber.server.get_slumber_directory',
                lambda: 'http://localhost:8008/somewhere/slumber/'):
            self.assertEqual(get_slumber_local_url_prefix(),
                'http://localhost:8008/')

    def test_slumber_local_url_https(self):
        with patch('slumber.server.get_slumber_directory',
                lambda: 'https://example.com/somewhere/slumber/'):
            self.assertEqual(get_slumber_local_url_prefix(),
                'https://example.com/')

    def test_slumber_local_url_with_services(self):
        with patch('slumber.server.get_slumber_directory', lambda: {
                'pizzas': 'http://localhost:8000:/slumber/pizzas/',
                'takeaway': 'http://localhost:8002:/slumber/'}):
            with patch('slumber.server.get_slumber_service', lambda: 'pizzas'):
                self.assertEqual(get_slumber_local_url_prefix(),
                'http://localhost:8000:/')

    def test_slumber_local_url_with_services_but_no_service_specified(self):
        with patch('slumber.server.get_slumber_directory', lambda: {
                'pizzas': 'http://localhost:8000:/slumber/pizzas/',
                'takeaway': 'http://localhost:8002:/slumber/'}):
            with self.assertRaises(NoServiceSpecified):
                self.assertEqual(get_slumber_local_url_prefix(),
                'http://localhost:8000:/')

    def test_slumber_local_url_with_services_but_relative_self_service_url(self):
        with patch('slumber.server.get_slumber_directory', lambda: {
                'pizzas': '/slumber/pizzas/',
                'takeaway': 'http://localhost:8002:/slumber/'}):
            with patch('slumber.server.get_slumber_service', lambda: 'pizzas'):
                with self.assertRaises(AbsoluteURIRequired):
                    self.assertEqual(get_slumber_local_url_prefix(),
                    'http://localhost:8000:/')

    def test_application_repr(self):
        model = DJANGO_MODEL_TO_SLUMBER_MODEL[Pizza]
        self.assertEqual(str(model), "slumber_examples.Pizza")
        self.assertEqual(str(model.app), "slumber_examples")


class TestRequirePermissions(ConfigureUser, TestCase):
    def setUp(self):
        super(TestRequirePermissions, self).setUp()
        self.request = Mock()
        self.request.user = self.user
        self.has_perm = self.request.user.has_perm
        self.request.user.has_perm = Mock()

    def tearDown(self):
        super(TestRequirePermissions, self).tearDown()
        self.request.user.has_perm = self.has_perm

    def test_require_permissions__have_no_permission(self):
        view = Mock(return_value='fake response')
        required_permissions = ['test_permission1', 'test_permission2']
        self.request.user.has_perm.return_value = False

        decorator = require_permissions(required_permissions)
        decorated = decorator(view)
        with self.assertRaises(Forbidden):
            decorated(self, self.request)

    def test_require_permissions__have_all_required_permissions(self):
        view = Mock(return_value='fake response')
        required_permissions = ['test_permission1', 'test_permission2']
        self.request.user.has_perm.return_value = True

        decorator = require_permissions(required_permissions)
        decorated = decorator(view)
        decorated(self, self.request)

        # It will check each permission in the list.
        self.assertEqual(self.request.user.has_perm.call_count, len(required_permissions))
        self.request.user.has_perm.assert_any_call(required_permissions[0])
        self.request.user.has_perm.assert_any_call(required_permissions[1])

        # After the permissions are checked, it will call the view function.
        view.assert_called_once_with(self, self.request)
