from django.test import TestCase

from slumber.connector.ua import get

from slumber_examples.models import Shop
from slumber_examples.tests.configurations import ConfigureUser

class TestJSON(ConfigureUser, TestCase):

    def setUp(self):
        super(TestJSON, self).setUp()
        self.old_value = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_value
        super(TestJSON, self).tearDown()

    def test_as_json(self):
        # Arrange
        request = {}
        response = {'_meta': dict(status=200, message='OK'),
                    'fake_content': 'sputnik'}
        content_type = 'application/json'

        expected_content_type = "%s; charset=utf-8" % content_type
        expected_response = HttpResponse(request, expected_content_type, 200)

        # Act
        http_response = as_json(request, response, content_type)

        # Assert
        self.assertEqual(str(http_response), str(expected_response))


    def test_as_json_should_not_append_charset_if_its_provided(self):
        # Arrange
        request = {}
        response = {'_meta': dict(status=200, message='OK'),
                    'fake_content': 'sputnik'}
        content_type = 'application/json; charset=utf-16'

        # Act
        http_response = as_json(request, response, content_type)

        # Assert
        self.assertEqual(http_response['Content-Type'], 'application/json; charset=utf-16')
