from simplejson import loads

from django.test import TestCase
from django.test.client import Client

from slumber_test.models import Pizza, PizzaPrice


class TestBasicViews(TestCase):

    def do_get(self, url, query = {}):
        response = self.client.get(url, query,
            HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
        if response.status_code == 200:
            return response, loads(response.content)
        else:
            return response, {}

    def do_post(self, url, body):
        response = self.client.post(url, body,
            HTTP_HOST='localhost', REMOTE_ADDR='127.0.0.1')
        if response.status_code == 200:
            return response, loads(response.content)
        else:
            return response, {}


    def test_applications(self):
        response, json = self.do_get('/slumber/')
        apps = json['apps']
        self.assertEquals(apps['slumber_test'], '/slumber/slumber_test/')

    def test_model_search_success(self):
        response, json = self.do_get('/slumber/', {'model': 'slumber_test.Pizza'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'],
            'http://localhost/slumber/slumber_test/Pizza/')

    def test_model_search_invalid(self):
        response, json = self.do_get('/slumber/', {'model': 'nota.model'})
        self.assertEquals(response.status_code, 404)


    def test_application_with_models(self):
        response, json = self.do_get('/slumber/slumber_test/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json['models']))
        self.assertEquals(json['models']['Pizza'],
            '/slumber/slumber_test/Pizza/')


    def test_application_without_models(self):
        response, json = self.do_get('/slumber/slumber_test/no_models/')
        self.assertEquals(response.status_code, 200)
        self.assertFalse(len(json['models']))


    def test_instance_metadata_pizza(self):
        response, json = self.do_get('/slumber/slumber_test/Pizza/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('for_sale'))
        self.assertEquals(json['fields']['for_sale']['type'],
            'django.db.models.fields.BooleanField')
        self.assertEquals(json['operations']['instances'],
            '/slumber/slumber_test/Pizza/instances/')
        self.assertFalse(json['operations'].has_key('data'), json['operations'])
        self.assertTrue(json['operations'].has_key('get'), json['operations'])

    def test_instance_metadata_pizzaprice(self):
        response, json = self.do_get('/slumber/slumber_test/PizzaPrice/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('pizza'))
        self.assertEquals(json['fields']['pizza']['type'],
            '/slumber/slumber_test/Pizza/')


    def test_instance_puttable(self):
        response, json = self.do_get('/slumber/slumber_test/Pizza/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['puttable'], [['id'], ['name']])


    def test_model_operation_instances_no_instances(self):
        response, json = self.do_get('/slumber/slumber_test/Pizza/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)

    def test_model_operation_instances_one_instance(self):
        Pizza(name='S1', for_sale=True).save()
        response, json = self.do_get('/slumber/slumber_test/Pizza/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 1)

    def test_model_operation_instances_twelve_instances(self):
        for i in range(12):
            Pizza(name='S%s' % i, for_sale=True).save()
        response, json = self.do_get('/slumber/slumber_test/Pizza/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 10)
        self.assertEquals(json['next_page'],
            '/slumber/slumber_test/Pizza/instances/?start_after=3')
        response, json = self.do_get('/slumber/slumber_test/Pizza/instances/',
            {'start_after': '3'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 2)
        self.assertEquals(json['next_page'],
            '/slumber/slumber_test/Pizza/instances/?start_after=1')
        response, json = self.do_get('/slumber/slumber_test/Pizza/instances/',
            {'start_after': '1'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)
        self.assertFalse(json.has_key('next_page'), json)


    def test_instance_creation_get(self):
        response, json = self.do_get('/slumber/slumber_test/Pizza/create/')
        self.assertFalse(json['created'], json)

    def test_instance_creation_post(self):
        response, json = self.do_post('/slumber/slumber_test/Pizza/create/',
            {'name': 'Test Pizza'})
        self.assertTrue(json['created'])
        self.assertEquals(Pizza.objects.count(), 1)
        self.assertEquals(Pizza.objects.all()[0].name, 'Test Pizza')


    def test_get_instance(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        response, json = self.do_get('/slumber/slumber_test/Pizza/')
        get_url = json['operations']['get']
        self.assertEquals(get_url, '/slumber/slumber_test/Pizza/get/')
        response, json = self.do_get(get_url, {'pk': s.pk})
        self.assertEquals(response.status_code, 302, response)
        self.assertEquals(response['location'],
            'http://localhost/slumber/slumber_test/Pizza/data/%s/' % s.pk)

    def test_instance_data_pizza(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        response, json = self.do_get('/slumber/slumber_test/Pizza/data/%s/' % s.pk)
        self.maxDiff = None
        self.assertEquals(json, dict(
            fields=dict(
                id=dict(data=s.pk, type='django.db.models.fields.AutoField'),
                for_sale=dict(data=s.for_sale, type='django.db.models.fields.BooleanField'),
                max_extra_toppings=dict(data=s.max_extra_toppings, type='django.db.models.fields.IntegerField'),
                name=dict(data=s.name, type='django.db.models.fields.CharField')),
            display='S1',
            data_arrays=dict(
                prices='/slumber/slumber_test/Pizza/data/%s/prices/' % s.pk)))

    def test_instance_data_pizzaprice(self):
        s = Pizza(name='p1', for_sale=True)
        s.save()
        p = PizzaPrice(pizza=s, date='2010-01-01', amount="13.95")
        p.save()
        response, json = self.do_get('/slumber/slumber_test/PizzaPrice/data/%s/' % p.pk)
        self.assertEquals(json, dict(display="PizzaPrice object",
            fields=dict(
                id={'data': 1, 'kind': 'value', 'type': 'django.db.models.fields.AutoField'},
                pizza={'data': {},
                    'kind': 'object', 'type': '/slumber/slumber_test/Pizza/'},
                date={'data': '2010-01-01', 'kind': 'value', 'type': 'django.db.models.fields.DateField'},
                amount={'data': '13.95', 'kind': 'value', 'type': 'django.db.models.fields.DecimalField'},
            ),
            data_arrays={}), json)

    def test_instance_data_array(self):
        s = Pizza(name='P', for_sale=True)
        s.save()
        for p in range(15):
            PizzaPrice(pizza=s, amount=str(p), date='2011-04-%s' % (p+1)).save()
        response, json = self.do_get('/slumber/slumber_test/Pizza/data/%s/prices/' % s.pk)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 10, json)
        self.assertTrue(json.has_key('next_page'), json)
        self.assertEquals(json['next_page'],
            '/slumber/slumber_test/Pizza/data/1/prices/?start_after=6',
            json['next_page'])
        response, json = self.do_get('/slumber/slumber_test/Pizza/data/1/prices/',
            {'start_after': '6'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 5)
        self.assertEquals(json['page'][0],
            {'pk': 5, 'data': '/slumber/slumber_test/PizzaPrice/data/5/', 'display': 'PizzaPrice object'})
        self.assertEquals(json['next_page'],
            '/slumber/slumber_test/Pizza/data/1/prices/?start_after=1')
        response, json = self.do_get('/slumber/slumber_test/Pizza/data/1/prices/',
            {'start_after': '1'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)
        self.assertFalse(json.has_key('next_page'))
