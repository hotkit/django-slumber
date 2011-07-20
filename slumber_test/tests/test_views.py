from simplejson import loads

from django.test import TestCase
from django.test.client import Client

from slumber_test.models import Pizza


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


    def test_instance_metadata(self):
        response, json = self.do_get('/slumber/slumber_test/Pizza/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(json['fields'].has_key('for_sale'))
        self.assertEquals(json['fields']['for_sale']['type'],
            'django.db.models.fields.BooleanField')
        self.assertEquals(json['operations']['instances'],
            '/slumber/slumber_test/Pizza/instances/')
        self.assertFalse(json['operations'].has_key('data'), json['operations'])


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


    #def test_instance_creation_get(self):
        #response, json = self.do_get('/slumber/bmf/core/Service/create/')
        #self.assertFalse(json['created'], json)

    #def test_instance_creation_post(self):
        #response, json = self.do_post('/slumber/bmf/core/Service/create/',
            #{'name': 'TestService'})
        #self.assertTrue(json['created'])
        #self.assertEquals(Service.objects.count(), 1)
        #self.assertEquals(Service.objects.all()[0].name, 'TestService')


    #def test_instance_data(self):
        #s = Service(name='S1').saved()
        #response, json = self.do_get('/slumber/bmf/core/Service/data/%s/' % s.pk)
        #self.assertEquals(json, dict(
            #fields=dict(
                #id=dict(data=s.pk, type='django.db.models.fields.AutoField'),
                #name=dict(data=s.name, type='django.db.models.fields.CharField')),
            #display='S1',
            #data_arrays=dict(
                    #itemgroup='/slumber/bmf/core/Service/data/1/itemgroup/',
                    #itemgroupservice='/slumber/bmf/core/Service/data/1/itemgroupservice/',
                    #mailinglist='/slumber/bmf/core/Service/data/1/mailinglist/',
                    #promocodetemplate='/slumber/bmf/core/Service/data/1/promocodetemplate/')))
