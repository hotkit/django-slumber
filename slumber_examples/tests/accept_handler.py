from mock import patch, Mock
from simplejson import loads, dumps
from django.http import HttpResponse
from django.test import TestCase
from slumber.server import accept_handler
from slumber.server.http import view_handler
from slumber.server import xml
from slumber.server import html
from django.conf import settings


class TestAcceptHandler(TestCase):
    def setUp(self):
        class Request(object):
            META = {'HTTP_ACCEPT': 'application/xml;', 'CONTENT_TYPE': None}
        self.request = Request()
        self.response = {'_meta': {'status': 200}}

    def test_accept_handler(self):
        content_type, handler = accept_handler.accept(self.request.META['HTTP_ACCEPT'])
        expect_http_response = handler(self.request, self.response, self.request.META.get('CONTENT_TYPE', None))
        self.assertTrue(isinstance(expect_http_response, HttpResponse))

    def test_accept_handler_with_content(self):
        test_str = {'test_value': 'hello'}
        accept_handlers_list = [
            ('application/json', lambda req, res, ct: HttpResponse(dumps(test_str), 'text/plain', status=200))
        ]
        fake_accept_str = 'text/*; application/json;'
        content_type, handler = accept_handler.accept(fake_accept_str, accept_handlers_list)
        expect_http_response = handler(self.request, self.response, self.request.META.get('CONTENT_TYPE', None))
        self.assertTrue(isinstance(expect_http_response, HttpResponse))
        self.assertEqual(loads(expect_http_response.content), test_str)

    def test_accept_handler_with_mix_value(self):
        accept_handlers_list = [
            ('application/json', lambda req, res, ct: None),
            ('application/xhtml', lambda req, res, ct: HttpResponse(dumps({'fake_fn2': True}), 'text/plain', status=200))
        ]
        fake_accept_str = 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
        content_type, handler = accept_handler.accept(fake_accept_str, accept_handlers_list)
        expect_http_response = handler(self.request, self.response, self.request.META.get('CONTENT_TYPE', None))
        self.assertTrue(isinstance(expect_http_response, HttpResponse))
        self.assertEqual(loads(expect_http_response.content), {'fake_fn2': True})


class TestUsingAcceptHandler(TestCase):
    def setUp(self):
        class Request(object):
            META = {'HTTP_ACCEPT': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;'}
            class user(object):
                @classmethod
                def is_authenticated(cls):
                    return True
                username = 'testuser'
        self.test_request = Request

    @patch('slumber.server.accept_handler.get_handlers_list')
    def test_with_accept_handler_with_default(self, mock_handler_list):
        settings.DEBUG = False
        test_str = 'just a fake content'
        mock_handler_list.return_value = []
        test_result_str = '{"_meta": {"status": 200, "username": "testuser", "message": "OK"}, "fake_content": "just a fake content"}'


        @view_handler
        def view(request, response):
            response['fake_content'] = test_str

        http_response = view( self.test_request() )

        self.assertEqual(test_result_str, str(http_response.content))

    @patch('slumber.server.accept_handler.get_handlers_list')
    def test_with_accept_header_value(self, mock_handler_list):
        test_str = 'just a fake content'

        mock_handler_list.return_value = [
            ('application/xml', lambda req, res, ct: HttpResponse(dumps(res), 'text/plain')),
        ]

        @view_handler
        def view(request, response):
            response['fake_content'] = test_str

        http_response = view( self.test_request() )
        content = loads(http_response.content)
        self.assertEquals(content, dict(
            fake_content=str(test_str),
            _meta=dict(status=200, message="OK", username="testuser")))

    @patch('slumber.server.accept_handler.get_handlers_list')
    def test_with_accept_header_as_xml(self, mock_handler_list):
        xml.as_xml = Mock()
        test_str = 'just a fake content'

        mock_handler_list.return_value = [
            ('application/json', lambda req, res, ct: HttpResponse(dumps(res), 'text/plain')),
            ('application/xml', xml.as_xml),
        ]

        @view_handler
        def view(request, response):
            response['fake_content'] = test_str

        view(self.test_request())
        self.assertTrue(xml.as_xml.called)

    @patch('slumber.server.accept_handler.get_handlers_list')
    def test_with_accept_handler_as_html(self, mock_handler_list):
        html.build_html = Mock()
        test_str = 'just a fake content'

        mock_handler_list.return_value = [
            ('application/json', lambda req, res, ct: HttpResponse(dumps(res), 'text/plain')),
            ('text/html', html.build_html),
        ]

        @view_handler
        def view(request, response):
            response['fake_content'] = test_str

        view( self.test_request() )
        self.assertTrue(html.build_html.called)
