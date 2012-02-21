from unittest2 import TestCase
from slumber.scheme import to_slumber_scheme


class URLHandling(TestCase):
    def test_not_a_service(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/', 'not_a_service',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_is_a_service(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/testservice/Model/', 'testservice',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'slumber://testservice/Model/')

    def test_wrong_url_prefix(self):
        translated = to_slumber_scheme(
            'http://www.example.com/slumber/testservice/Model/', 'testservice',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://www.example.com/slumber/testservice/Model/')
