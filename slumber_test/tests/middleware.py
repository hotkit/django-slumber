from django.test import TestCase


class TestMiddleware(TestCase):
    def test_request(self):
        response = self.client.get('/')
