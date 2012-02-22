from unittest2 import TestCase
from slumber.scheme import to_slumber_scheme, from_slumber_scheme, \
    SlumberServiceURLError


class URLHandlingToDatabase(TestCase):
    def test_no_services_pass_url_unchanged(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/', None)
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_not_a_service(self):
        translated = to_slumber_scheme(
            'http://example.org/slumber/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.org/slumber/')

    def test_is_a_service(self):
        translated = to_slumber_scheme(
            'http://example.com/slumber/testservice/Model/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'slumber://testservice/Model/')

    def test_ambiguous_prefix(self):
        translated = to_slumber_scheme(
            'http://www.example.com/slumber/testservice/Model/',
            dict(a='http://www.example.com/slumber/testservice/',
                testmodel='http://www.example.com/slumber/testservice/Model/'))
        self.assertEquals(translated, 'slumber://testmodel/')


class URLHandlingFromDatabase(TestCase):
    def test_no_services_with_normal_url(self):
        translated = from_slumber_scheme(
            'http://example.com/slumber/', None)
        self.assertEquals(translated,
            'http://example.com/slumber/')

    def test_no_services_with_slumber_url(self):
        with self.assertRaises(SlumberServiceURLError):
            translated = from_slumber_scheme(
                'slumber://service/Model/', None)

    def test_not_a_slumber_url(self):
        translated = from_slumber_scheme(
            'http://example.org/slumber/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.org/slumber/')

    def test_slumber_service_url(self):
        translated = from_slumber_scheme(
            'slumber://testservice/Model/',
            dict(testservice='http://example.com/slumber/testservice/'))
        self.assertEquals(translated,
            'http://example.com/slumber/testservice/Model/')

    def test_slumber_service_url_with_a_different_service(self):
        translated = from_slumber_scheme(
            'slumber://another_service/Model/',
            dict(testservice='http://example.com/slumber/testservice/',
                another_service='http://example.com/slumber/another_service/'))
        self.assertEquals(translated,
            'http://example.com/slumber/another_service/Model/')

    def test_slumber_service_url_with_invalid_service(self):
        with self.assertRaises(SlumberServiceURLError):
            from_slumber_scheme(
                'slumber://not-a-service/Model/',
                dict(testservice='http://example.com/slumber/testservice/'))
