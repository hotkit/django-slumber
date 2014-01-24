from __future__ import absolute_import

import dicttoxml
from xml.dom.minidom import parseString

from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase

from slumber.server.xml import as_xml
from slumber_examples.tests import ConfigureUser


class TestXML(ConfigureUser, TestCase):
    def setUp(self):
        super(TestXML, self).setUp()
        self.old_value = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_value
        super(TestXML, self).tearDown()

    def test_as_xml(self):
        # Arrange
        request = {}
        response = {'_meta': dict(status=200, message='OK'),
                    'fake_content': 'sputnik'}
        content_type = 'text/xml'

        xml_snippet = dicttoxml.dicttoxml(response, root=True)
        dom = parseString(xml_snippet).toprettyxml()

        expected_response = HttpResponse(dom, content_type, 200)

        # Act
        http_response = as_xml(request, response, content_type)

        # Assert
        self.assertEqual(str(http_response), str(expected_response))

