from datetime import date
from unittest2 import TestCase

from slumber.server.http import view_handler


class TestJSON(TestCase):
    def test_unicode_attributes(self):
        @view_handler
        def view(request, response):
            response['u'] = date.today()
        http_response = view({})
        self.assertEquals(http_response.content,
            """{\n    "u": "2011-08-11",\n    "_meta": {\n        "status": 200,\n        "message": "OK"\n    }\n}""")
