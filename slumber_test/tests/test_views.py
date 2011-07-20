from simplejson import loads

from django.test import TestCase
from django.test.client import Client

from bmf.testutils.decorators import fixture

from bmf.core.models import Service


@fixture
class TestBasicViews(TestCase):
    def setUp(self):
        self.client = Client()


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
        response, json = self.do_get('/datacnx/')
        apps = json['apps']
        self.assertEquals(apps['bmf.customer'], '/datacnx/bmf/customer/')

    def test_model_search_success(self):
        response, json = self.do_get('/datacnx/', {'model': 'customer.Customer'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'],
            'http://localhost/datacnx/bmf/customer/Customer/')

    def test_model_search_invalid(self):
        response, json = self.do_get('/datacnx/', {'model': 'nota.model'})
        self.assertEquals(response.status_code, 404)


    def test_application_with_models(self):
        response, json = self.do_get('/datacnx/bmf/customer/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json['models']))
        self.assertEquals(json['models']['Customer'],
            '/datacnx/bmf/customer/Customer/')


    def test_application_without_models(self):
        response, json = self.do_get('/datacnx/bmf/rest/')
        self.assertEquals(response.status_code, 200)
        self.assertFalse(len(json['models']))


    def test_instance_metadata(self):
        response, json = self.do_get('/datacnx/bmf/customer/CustomerStatus/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('active'))
        self.assertEquals(json['fields']['active']['type'],
            'django.db.models.fields.BooleanField')
        self.assertEquals(json['operations']['instances'],
            '/datacnx/bmf/customer/CustomerStatus/instances/')
        self.assertFalse(json['operations'].has_key('data'), json['operations'])


    def test_instance_puttable(self):
        response, json = self.do_get('/datacnx/bmf/customer/FitnessTest/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json['puttable'], [['id'], ['customer', 'date']])


    def test_model_operation_instances_no_instances(self):
        response, json = self.do_get('/datacnx/bmf/customer/CustomerStatus/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)

    def test_model_operation_instances_one_instance(self):
        Service(name='S1').save()
        response, json = self.do_get('/datacnx/bmf/core/Service/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 1)

    def test_model_operation_instances_twelve_instances(self):
        for i in range(12):
            Service(name='S%s' % i).save()
        response, json = self.do_get('/datacnx/bmf/core/Service/instances/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 10)
        self.assertEquals(json['next_page'],
            '/datacnx/bmf/core/Service/instances/?start_after=3')
        response, json = self.do_get('/datacnx/bmf/core/Service/instances/',
            {'start_after': '3'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 2)
        self.assertEquals(json['next_page'],
            '/datacnx/bmf/core/Service/instances/?start_after=1')
        response, json = self.do_get('/datacnx/bmf/core/Service/instances/',
            {'start_after': '1'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json['page']), 0)
        self.assertFalse(json.has_key('next_page'), json)


    def test_instance_creation_get(self):
        response, json = self.do_get('/datacnx/bmf/core/Service/create/')
        self.assertFalse(json['created'], json)

    def test_instance_creation_post(self):
        response, json = self.do_post('/datacnx/bmf/core/Service/create/',
            {'name': 'TestService'})
        self.assertTrue(json['created'])
        self.assertEquals(Service.objects.count(), 1)
        self.assertEquals(Service.objects.all()[0].name, 'TestService')


    def test_instance_data(self):
        s = Service(name='S1').saved()
        response, json = self.do_get('/datacnx/bmf/core/Service/data/%s/' % s.pk)
        self.assertEquals(json, dict(
            fields=dict(
                id=dict(data=s.pk, type='django.db.models.fields.AutoField'),
                name=dict(data=s.name, type='django.db.models.fields.CharField')),
            display='S1',
            data_arrays=dict(
                    itemgroup='/datacnx/bmf/core/Service/data/1/itemgroup/',
                    itemgroupservice='/datacnx/bmf/core/Service/data/1/itemgroupservice/',
                    mailinglist='/datacnx/bmf/core/Service/data/1/mailinglist/',
                    promocodetemplate='/datacnx/bmf/core/Service/data/1/promocodetemplate/')))
