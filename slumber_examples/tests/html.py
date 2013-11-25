from django.http import HttpResponse
from django.test import TestCase
from mock import patch
import mock

from slumber.server.html import build_html, convert, convert_atom
from slumber_examples.tests import ConfigureUser


class TestHTML(ConfigureUser, TestCase):
    @patch("slumber.server.html.convert")
    def test_as_HTML_should_call_convert (self, convert_mocked):
        # Arrange
        request = {}
        response = {'_meta': dict(status=200, message='OK')}
        content_type = None
        convert_mocked.return_value = 'text'

        # Act
        build_html(request, response, content_type)

        # Assert
        self.assertTrue(convert_mocked.called)

    def test_convert_with_int_type(self):
        #Arrange
        test_dict = {'a':5}
        expect_result = '<dl><dt>a</dt><dd><span class="int">5</span></dd></dl>'
        #Act
        result = convert(test_dict)
        #Assert
        self.assertEqual(result, expect_result)

    def test_convert_with_float_type(self):
        #Arrange
        test_dict = {'a':5.55}
        expect_result = '<dl><dt>a</dt><dd><span class="float">5.55</span></dd></dl>'
        #Act
        result = convert(test_dict)
        #Assert
        self.assertEqual(result, expect_result)

    def test_convert_with_string_type(self):
        #Arrange
        test_dict = {'a':'Test_text'}
        expect_result = '<dl><dt>a</dt><dd><span class="string">Test_text</span></dd></dl>'
        #Act
        result = convert(test_dict)
        #Assert
        self.assertEqual(result, expect_result)

    def test_convert_with_array_type(self):
        #Arrange
        test_dict = {'a':[1, 2, 3]}
        expect_result = '<dl><dt>a</dt><dd><ol><li><span class="int">1</span></li><li><span class="int">2</span></li>' \
                        '<li><span class="int">3</span></li></ol></dd></dl>'
        #Act
        result = convert(test_dict)
        #Assert
        self.assertEqual(result, expect_result)

    def test_convert_with_none_type(self):
        #Arrange
        test_dict = {'a':None}
        expect_result = '<dl><dt>a</dt><dd><span class="null"></span></dd></dl>'
        #Act
        result = convert(test_dict)
        #Assert
        self.assertEqual(result, expect_result)

    def test_convert_with_boolean_type(self):
        #Arrange
        test_dict = {'a':True}
        expect_result = '<dl><dt>a</dt><dd><span class="boolean">True</span></dd></dl>'
        #Act
        result = convert(test_dict)
        #Assert
        self.assertEqual(result, expect_result)

    def test_convert_with_Mock_type(self):
        #Arrange
        test_dict = mock
        #Assert
        with self.assertRaises(TypeError) as e:
            convert(test_dict)

        self.assertEqual(e.exception.message, 'Unsupported data type')

    def test_convert_atom_with_Mock_type(self):
        #Arrange
        test_dict = mock
        #Assert
        with self.assertRaises(TypeError) as e:
            convert_atom(test_dict)

        self.assertEqual(e.exception.message, 'Unsupported data type')
