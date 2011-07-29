"""
    Implements the user agent used to communicate with the Slumber
    servers.
"""
from django.conf import settings
from django.test.client import Client as FakeClient

from httplib2 import Http
from simplejson import loads
from urlparse import parse_qs


_fake = FakeClient()
_http = Http()


def _parse_qs(url):
    """Split the query string off (this is needed to support Django 1.0's
    fake HTTP client.
    """
    if url.find('?') >= 0:
        path, query_string = url.split('?')
        return path, parse_qs(query_string)
    else:
        return url, {}


def get(url):
    """Perform a GET request against a Slumber server.
    """
    # Pylint gets confused by the fake HTTP client
    # pylint: disable=E1103
    slumber_local = getattr(settings, 'SLUMBER_LOCAL', 'http://localhost:8000/')
    if url.startswith(slumber_local):
        url_fragment = url[len(slumber_local) - 1:]
        file_spec, query = _parse_qs(url_fragment)
        response = _fake.get(file_spec, query,
            HTTP_HOST='localhost:8000')
        if response.status_code in [301, 302]:
            return get(response['location'])
        assert response.status_code == 200, (url_fragment, response)
        content = response.content
    else:
        response, content = _http.request(url)
        assert response.status == 200, url
    return response, loads(content)
