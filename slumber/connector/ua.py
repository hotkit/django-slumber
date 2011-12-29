"""
    Implements the user agent used to communicate with the Slumber
    servers.
"""
from django.core.cache import cache
from django.test.client import Client as FakeClient

from httplib2 import Http
from simplejson import loads
from urllib import urlencode
from urlparse import parse_qs


from slumber.server import get_slumber_local_url_prefix


_fake = FakeClient()


def _parse_qs(url):
    """Split the query string off (this is needed to support Django 1.0's
    fake HTTP client.
    """
    if url.find('?') >= 0:
        path, query_string = url.split('?')
        return path, parse_qs(query_string)
    else:
        return url, {}

def _use_fake(url):
    """Return the local URL fragment if the request should use the Fake
    HTTP client as it is local, otherwise return None
    """
    slumber_local = get_slumber_local_url_prefix()
    if url.startswith(slumber_local):
        return url[len(slumber_local) - 1:]
    elif url.startswith('/'):
        return url


def get(url, ttl = 0):
    """Perform a GET request against a Slumber server.
    """
    # Pylint gets confused by the fake HTTP client
    # pylint: disable=E1103
    url_fragment = _use_fake(url)
    if url_fragment:
        file_spec, query = _parse_qs(url_fragment)
        response = _fake.get(file_spec, query,
            HTTP_HOST='localhost:8000')
        if response.status_code in [301, 302]:
            return get(response['location'])
        assert response.status_code == 200, (url_fragment, response)
        content = response.content
    else:
        cache_key = 'slumber.connector.ua.get.%s' % url
        cached = cache.get(cache_key)
        if not cached:
            for _ in range(0, 3):
                response, content = Http().request(url)
                if response.status == 200:
                    break
            assert response.status == 200, url
            if ttl:
                cache.set(cache_key, (response, content), ttl)
        else:
            response, content = cached
            response.from_cache = True
    return response, loads(content)


def post(url, data):
    """Perform a POST request against a Slumber server.
    """
    url_fragment = _use_fake(url)
    if url_fragment:
        response = _fake.post(url_fragment, data, HTTP_HOST='localhost:8000')
        assert response.status_code == 200, \
            (url_fragment, response, response.content)
        content = response.content
    else:
        body = urlencode(data)
        response, content = Http().request(url, "POST", body=body)
        assert response.status == 200, url
    return response, loads(content)

