from datetime import date
from mock import patch
from unittest2 import TestCase

from slumber.server import get_slumber_services
from slumber.server.http import view_handler
from slumber.server.meta import get_application


class TestJSON(TestCase):
    def test_unicode_attributes(self):
        d = date.today()
        @view_handler
        def view(request, response):
            response['u'] = d
        http_response = view({})
        self.assertEquals(http_response.content,
            """{\n    "u": "%s",\n    "_meta": {\n        "status": 200,\n        "message": "OK"\n    }\n}""" %
                d)


class InternalAPIs(TestCase):
    def test_get_application(self):
        app = get_application('slumber_test')
        self.assertEqual(app.name, 'slumber_test')
        self.assertEqual(app.path, 'slumber_test')

    def test_slumber_services_none(self):
        directory = get_slumber_services()
        self.assertIsNone(directory)

    def test_slumber_services(self):
        with patch('slumber.server.get_slumber_directory', lambda: {
                'pizzas': '/slumber/pizzas/',
                'takeaway': 'http://localhost:8002:/slumber/'}):
            directory = get_slumber_services()
            self.assertIsNotNone(directory)

