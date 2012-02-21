from unittest2 import TestCase
from slumber.scheme import to_slumber_scheme, from_slumber_scheme


class URLHandling(TestCase):
    def test_not_a_service(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/', 'not_a_service',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_no_service_specified(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/', None,
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

    def test_not_a_slumber_url(self):
        translated = from_slumber_scheme(
            'http://example.com/slumber/', 'not_a_service',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_slumber_service_url(self):
        translated = from_slumber_scheme(
            'slumber://testservice/Model/', 'testservice',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.com/slumber/testservice/Model/')

    def test_slumber_service_url_without_giving_a_service(self):
        with self.assertRaises(NotImplementedError):
            from_slumber_scheme(
                'slumber://testservice/Model/', None,
                dict(testservice='http://example.com/slumber/testservice/'))

    def test_slumber_service_url_with_a_different_service(self):
        with self.assertRaises(NotImplementedError):
            from_slumber_scheme(
                'slumber://another_service/Model/', 'testservice',
                dict(testservice='http://example.com/slumber/testservice/',
                    another_service='http://example.com/slumber/another_service/'))

    def test_slumber_service_url_with_invalid_service(self):
        with self.assertRaises(NotImplementedError):
            from_slumber_scheme(
                'slumber://not-a-service/Model/', 'testservice',
                dict(testservice='http://example.com/slumber/testservice/'))
