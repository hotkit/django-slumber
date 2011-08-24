from datetime import date
from unittest2 import TestCase

from slumber.server.http import view_handler


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
