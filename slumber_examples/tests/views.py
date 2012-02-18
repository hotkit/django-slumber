from mock import patch
from simplejson import loads

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase

from slumber_examples.models import Pizza, PizzaPrice


def _perform(client, method, url, data):
    response = getattr(client, method)(url, data,
        HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
    if response.status_code == 200:
        return response, loads(response.content)
    else:
        return response, {}


class ViewTests(object):
    """Base class for view tests that give us some user agent functionality.
    """
    def do_get(self, url, query = {}):
        return _perform(self.client, 'get', self.url(url), query)

    def do_post(self, url, body):
        return _perform(self.client, 'post', self.url(url), body)

    def url(self, path):
        if not path.startswith(self.PREFIX + '/'):
            return self.PREFIX + path
        else:
            return path

class PlainTests(object):
    """Used to get non-service based view tests.
    """
    PREFIX = '/slumber'

class ServiceTests(object):
    """Used to get service based view tests.
    """
    PREFIX  = '/slumber/pizzas'
    def setUp(self):
        pizzas = lambda: 'pizzas'
        self.__patchers = [
            patch('slumber.server._get_slumber_service', pizzas),
        ]
        [p.start() for p in self.__patchers]
    def tearDown(self):
        [p.stop() for p in self.__patchers]


class ViewErrors(ViewTests):

    def test_method_error(self):
        response, json = self.do_post('/slumber_examples/Pizza/instances/', {})
        self.assertEquals(response.status_code, 403)

    def test_invalid_method(self):
        url = self.url('/slumber_examples/Pizza/instances/')
        response = self.client.get(url, REQUEST_METHOD='PURGE',
            HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
        self.assertEquals(response.status_code, 403, response.content)

    def test_missing_slash(self):
        response, json = self.do_get('/slumber_examples')
        self.assertEquals(response.status_code, 301)
        self.assertTrue(response['location'].endswith('/slumber_examples/'),
            response['location'])

    def test_invalid_model(self):
        response, json = self.do_get('/slumber_examples/not-a-model/')
        self.assertEquals(response.status_code, 404)

    def test_invalid_model_operation(self):
        response, json = self.do_get('/slumber_examples/Pizza/not-an-operation/')
        self.assertEquals(response.status_code, 404)

class ViewErrorsPlain(ViewErrors, PlainTests, TestCase):
    pass
class ViewErrorsService(ViewErrors, ServiceTests, TestCase):
    def test_invalid_service(self):
        response = self.client.get('/slumber/not-a-service/',
            HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
        self.assertEquals(response.status_code, 404, response.content)


class BasicViews(ViewTests):

    def test_applications(self):
        response, json = self.do_get('/')
        apps = json['apps']
        self.assertEquals(apps['slumber_examples'], self.url('/slumber_examples/'))

    def test_model_search_success(self):
        response, json = self.do_get('/', {'model': 'slumber_examples.Pizza'})
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['location'].endswith(
            '/slumber_examples/Pizza/'), response['location'])

    def test_model_search_invalid(self):
        response, json = self.do_get('/', {'model': 'nota.model'})
        self.assertEquals(response.status_code, 404)


    def test_application_with_models(self):
        response, json = self.do_get('/slumber_examples/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json['models']))
        self.assertEquals(json['models']['Pizza'],
            self.url('/slumber_examples/Pizza/'))


    def test_application_without_models(self):
        response, json = self.do_get('/slumber_examples/no_models/')
        self.assertEquals(response.status_code, 200)
        self.assertFalse(len(json['models']))


    def test_nested_application(self):
        response, json = self.do_get('/slumber_examples/nested1/')
        self.assertEquals(response.status_code, 200, 'slumber_examples.nested1')
    def test_doubly_nested_application(self):
        response, json = self.do_get('/slumber_examples/nested1/nested2/')
        self.assertEquals(response.status_code, 200, 'slumber_examples.nested1.nested2')


    def test_instance_metadata_pizza(self):
        response, json = self.do_get('/slumber_examples/Pizza/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('for_sale'))
        self.assertEquals(json['fields']['for_sale']['type'],
            'django.db.models.fields.BooleanField')
        self.assertEquals(json['operations']['instances'],
            self.url('/slumber_examples/Pizza/instances/'))
        self.assertFalse(json['operations'].has_key('data'), json['operations'])
        self.assertTrue(json['operations'].has_key('get'), json['operations'])

    def test_instance_metadata_pizzaprice(self):
        response, json = self.do_get('/slumber_examples/PizzaPrice/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('pizza'))
        self.assertEquals(json['fields']['pizza']['type'],
            self.url('/slumber_examples/Pizza/'))

    def test_model_metadata_user(self):
        response, json = self.do_get('/django/contrib/auth/User/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['operations'].has_key('authenticate'), json['operations'])
        self.assertEquals(json['operations']['authenticate'],
            self.url('/django/contrib/auth/User/authenticate/'))

    def test_instance_metadata_user(self):
        user = User(username='test-user')
        user.save()
        response, json = self.do_get('/django/contrib/auth/User/data/%s/' %
            user.pk)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['operations'].has_key('has-permission'), json['operations'])


    def test_instance_puttable(self):
        response, json = self.do_get('/slumber_examples/Pizza/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['puttable'], [['id'], ['name']])


    def test_model_operation_instances_no_instances(self):
        response, json = self.do_get('/slumber_examples/Pizza/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)

    def test_model_operation_instances_one_instance(self):
        Pizza(name='S1', for_sale=True).save()
        response, json = self.do_get('/slumber_examples/Pizza/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 1)

    def test_model_operation_instances_twelve_instances(self):
        for i in range(12):
            Pizza(name='S%s' % i, for_sale=True).save()
        response, json = self.do_get('/slumber_examples/Pizza/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 10)
        self.assertEquals(json['next_page'],
            self.url('/slumber_examples/Pizza/instances/?start_after=3'))
        response, json = self.do_get('/slumber_examples/Pizza/instances/',
            {'start_after': '3'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 2)
        self.assertEquals(json['next_page'],
            self.url('/slumber_examples/Pizza/instances/?start_after=1'))
        response, json = self.do_get('/slumber_examples/Pizza/instances/',
            {'start_after': '1'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)
        self.assertFalse(json.has_key('next_page'), json)


    def test_instance_creation_get(self):
        response, json = self.do_get('/slumber_examples/Pizza/create/')
        self.assertEquals(response.status_code, 403, response.content)

    def test_instance_creation_post(self):
        response, json = self.do_post('/slumber_examples/Pizza/create/',
            {'name': 'Test Pizza', 'for_sale': ''})
        self.assertTrue(json.get('identity', '').endswith(
            '/slumber_examples/Pizza/data/1/'), json)
        self.assertEquals(Pizza.objects.count(), 1)
        self.assertEquals(Pizza.objects.all()[0].name, 'Test Pizza')
        self.assertFalse(Pizza.objects.all()[0].for_sale)


    def test_update_instance(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        response, json = self.do_post('/slumber_examples/Pizza/update/1/', {
            'name': 'New pizza'})
        self.assertEquals(response.status_code, 302)
        n = Pizza.objects.get(pk=1)
        self.assertEquals(n.name, "New pizza")


    def test_get_instance(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        response, json = self.do_get('/slumber_examples/Pizza/')
        get_url = json['operations']['get']
        self.assertEquals(get_url, self.url('/slumber_examples/Pizza/get/'))
        def check_query(query):
            response, json = self.do_get(get_url, query)
            self.assertEquals(response.status_code, 200, response)
            self.assertTrue(json['identity'].endswith(
                '/slumber_examples/Pizza/data/%s/' % s.pk), response)
        check_query({'pk': s.pk})
        check_query({'id': s.pk})
        check_query({'name': s.name})

    def test_instance_data_pizza(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        response, json = self.do_get('/slumber_examples/Pizza/data/%s/' % s.pk)
        self.maxDiff = None
        self.assertEquals(json, dict(
            _meta={'message': 'OK', 'status': 200},
            type=self.url('/slumber_examples/Pizza/'),
            identity=self.url('/slumber_examples/Pizza/data/1/'),
            display='S1',
            operations=dict(
                data=self.url('/slumber_examples/Pizza/data/1/'),
                delete=self.url('/slumber_examples/Pizza/delete/1/'),
                update=self.url('/slumber_examples/Pizza/update/1/')),
            fields=dict(
                id=dict(data=s.pk, kind='value', type='django.db.models.fields.AutoField'),
                for_sale=dict(data=s.for_sale, kind='value', type='django.db.models.fields.BooleanField'),
                max_extra_toppings=dict(data=s.max_extra_toppings, kind='value', type='django.db.models.fields.IntegerField'),
                name=dict(data=s.name, kind='value', type='django.db.models.fields.CharField'),
                exclusive_to={'data': None, 'kind': 'object', 'type': self.url('/slumber_examples/Shop/')}),
            data_arrays=dict(
                prices=self.url('/slumber_examples/Pizza/data/%s/prices/' % s.pk))))

    def test_instance_data_pizzaprice(self):
        s = Pizza(name='p1', for_sale=True)
        s.save()
        p = PizzaPrice(pizza=s, date='2010-01-01')
        p.save()
        response, json = self.do_get('/slumber_examples/PizzaPrice/data/%s/' % p.pk)
        self.assertEquals(json, dict(
            _meta={'message': 'OK', 'status': 200},
            type=self.url('/slumber_examples/PizzaPrice/'),
            identity=self.url('/slumber_examples/PizzaPrice/data/1/'),
            display="PizzaPrice object",
            operations=dict(
                data=self.url('/slumber_examples/PizzaPrice/data/1/'),
                delete=self.url('/slumber_examples/PizzaPrice/delete/1/'),
                update=self.url('/slumber_examples/PizzaPrice/update/1/')),
            fields=dict(
                id={'data': 1, 'kind': 'value', 'type': 'django.db.models.fields.AutoField'},
                pizza={'data': {
                        'type': self.url('/slumber_examples/Pizza/'), 'display':'p1',
                        'data': self.url('/slumber_examples/Pizza/data/1/')},
                    'kind': 'object', 'type': self.url('/slumber_examples/Pizza/')},
                date={'data': '2010-01-01', 'kind': 'value', 'type': 'django.db.models.fields.DateField'},
            ),
            data_arrays={'amounts': self.url('/slumber_examples/PizzaPrice/data/1/amounts/')}))

    def test_instance_data_array(self):
        s = Pizza(name='P', for_sale=True)
        s.save()
        for p in range(15):
            PizzaPrice(pizza=s, date='2011-04-%s' % (p+1)).save()
        response, json = self.do_get('/slumber_examples/Pizza/data/%s/prices/' % s.pk)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 10, json)
        self.assertTrue(json.has_key('next_page'), json)
        self.assertEquals(json['next_page'],
            self.url('/slumber_examples/Pizza/data/1/prices/?start_after=6'),
            json['next_page'])
        response, json = self.do_get('/slumber_examples/Pizza/data/1/prices/',
            {'start_after': '6'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 5)
        self.assertEquals(json['page'][0], {
            'type': self.url('/slumber_examples/PizzaPrice/'),
            'pk': 5, 'data': self.url('/slumber_examples/PizzaPrice/data/5/'), 'display': 'PizzaPrice object'})
        self.assertFalse(json.has_key('next_page'), json.keys())


    def test_delete_instance(self):
        s = Pizza(name='P')
        s.save()
        response, json = self.do_get('/slumber_examples/Pizza/data/%s/' % s.pk)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['operations'].has_key('delete'), json['operations'])
        response, json = self.do_post(json['operations']['delete'], {})
        self.assertEquals(response.status_code, 200)
        with self.assertRaises(Pizza.DoesNotExist):
            Pizza.objects.get(pk=s.pk)

class BasicViewsPlain(BasicViews, PlainTests, TestCase):
    pass
class BasicViewsService(BasicViews, ServiceTests, TestCase):
    def test_services_with_directory(self):
        with patch('slumber.server.get_slumber_directory', lambda: {
                'pizzas': 'http://localhost:8000:/slumber/pizzas/',
                'takeaway': 'http://localhost:8002:/slumber/'}):
            response = self.client.get('/slumber/',
                HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
        json = loads(response.content)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(json['services'].get('pizzas', None),
            'http://localhost:8000:/slumber/pizzas/', json)
        self.assertEqual(json['services'].get('takeaway', None),
            'http://localhost:8002:/slumber/', json)

    def test_services_without_directory(self):
        response = self.client.get('/slumber/',
            HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
        json = loads(response.content)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(json['services'].get('pizzas', None), '/slumber/pizzas/', json)


class UserViews(ViewTests):
    authn = '/django/contrib/auth/User/authenticate/'
    data = '/django/contrib/auth/User/data/%s/'
    perm = '/django/contrib/auth/User/has-permission/%s/%s/'
    perms = '/django/contrib/auth/User/get-permissions/%s/'

    def setUp(self):
        self.user = User(username='test-user')
        self.user.set_password('password')
        self.user.save()
        super(UserViews, self).setUp()

    def test_user_data(self):
        response, json = self.do_get(self.data % self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn('is_superuser', json['fields'].keys())
        self.assertIn('date_joined', json['fields'].keys())

    def test_user_not_found(self):
        response, json = self.do_post(self.authn, dict(username='not-a-user', password=''))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['authenticated'], False, json)
        self.assertIsNone(json['user'], json)

    def test_user_wrong_password(self):
        response, json = self.do_post(self.authn,
            dict(username=self.user.username, password='wrong'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['authenticated'], False, json)
        self.assertIsNone(json['user'], json)

    def test_user_authenticates(self):
        response, json = self.do_post(self.authn,
            dict(username=self.user.username, password='password'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['authenticated'], True, json)
        self.assertDictContainsSubset(
            {'pk': self.user.pk, 'display_name': 'test-user'},
            json['user'])
        self.assertTrue(
            json['user']['url'].endswith('/django/contrib/auth/User/data/1/'),
            json['user']['url'])

    def test_user_permission_no_permission(self):
        response, json = self.do_get(self.perm % (self.user.pk, 'foo.example'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['is-allowed'], False, json)

    def test_user_permission_is_allowed(self):
        permission = Permission(content_type_id=1, name='Can something',
            codename='can_something')
        permission.save()
        self.user.user_permissions.add(permission)
        response, json = self.do_get(self.perm % (self.user.pk, 'auth.can_something'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['is-allowed'], True, json)

    def test_user_permission_not_allowed(self):
        permission = Permission(content_type_id=1, name='Can something',
            codename='can_something')
        permission.save()
        response, json = self.do_get(self.perm % (self.user.pk, 'auth.can_something'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['is-allowed'], False, json)

    def test_get_group_permissions(self):
        response, json = self.do_get(self.perms % self.user.pk)
        self.assertEquals(response.status_code, 200)
        self.assertItemsEqual(json['group_permissions'], [])


class UserViewsPlain(UserViews, PlainTests, TestCase):
    pass
class UserViewsService(UserViews, ServiceTests, TestCase):
    pass

