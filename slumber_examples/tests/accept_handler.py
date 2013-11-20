from mock import patch
from simplejson import loads, dumps
from django.http import HttpResponse
from django.test import TestCase
from slumber.server import accept_handler
from slumber.server.http import view_handler


class TestAcceptHandler(TestCase):
    def setUp(self):
        class Request(object):
            META = {'accept': None, 'CONTENT_TYPE': None}
        self.request = Request()
        self.response = {'_meta': {'status': 200}}

    def test_accept_handler(self):
        expect_http_response = accept_handler.accept(self.request.META['accept'])(
            self.request, self.response, self.request.META.get('CONTENT_TYPE', None)
        )
        self.assertTrue(isinstance(expect_http_response, HttpResponse))

    def test_accept_handler_with_content(self):
        test_str = {'test_value': 'hello'}
        accept_handlers_list = [
            ('application/json', lambda req, res, ct: HttpResponse(dumps(test_str), 'text/plain', status=200))
        ]
        fake_accept_str = 'text/*; application/json;'
        expect_http_response = accept_handler.accept(fake_accept_str, accept_handlers_list)(
            self.request, self.response, self.request.META.get('CONTENT_TYPE', None)
        )
        self.assertTrue(isinstance(expect_http_response, HttpResponse))
        self.assertEqual(loads(expect_http_response.content), test_str)

    def test_accept_handler_with_real_value(self):
        accept_handlers_list = [
            ('application/json', lambda req, res, ct: None),
            ('application/xhtml', lambda req, res, ct: HttpResponse(dumps({'fake_fn2': True}), 'text/plain', status=200))
        ]
        fake_accept_str = 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
        expect_http_response = accept_handler.accept(fake_accept_str, accept_handlers_list)(
            self.request, self.response, self.request.META.get('CONTENT_TYPE', None)
        )
        self.assertTrue(isinstance(expect_http_response, HttpResponse))
        self.assertEqual(loads(expect_http_response.content), {'fake_fn2': True})


class TestUsingAcceptHandler(TestCase):
    @patch('slumber.server.accept_handler.get_handlers_list')
    def test_with_accept_header_value(self, mock_handler_list):
        test_str = 'just a fake content'
        class Request(object):
            META = {'accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;'}
            class user(object):
                @classmethod
                def is_authenticated(cls):
                    return True
                username = 'testuser'

        mock_handler_list.return_value = [
            ('application/xml', lambda req, res, ct: HttpResponse(dumps(res), 'text/plain')),
        ]

        @view_handler
        def view(request, response):
            response['fake_content'] = test_str

        http_response = view(Request())
        content = loads(http_response.content)
        self.assertEquals(content, dict(
            fake_content=str(test_str),
            _meta=dict(status=200, message="OK", username="testuser")))

