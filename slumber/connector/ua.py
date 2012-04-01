"""
    Implements the user agent used to communicate with the Slumber
    servers.
"""
from django.core.cache import cache
from django.test.client import Client as FakeClient

from datetime import datetime
from fost_authn.signature import fost_hmac_request_signature
from httplib2 import Http
import logging
from simplejson import loads
from urllib import quote, urlencode
from urlparse import parse_qs

from slumber._caches import PER_THREAD
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


def _sign_request(method, url, body = ''):
    """Calculate the request headers that need to be added so that the
    request is properly signed and the Slumber server will consider
    the current user to be authenticated.
    """
    logging.info(u'%s\n%s', type(body), body)
    headers = {}
    request = getattr(PER_THREAD, 'request', None)
    if request and request.user.is_authenticated():
        if type(body) == unicode:
            body = body.encode('utf-8')
        now = datetime.utcnow().isoformat() + 'Z'
        _, signature = fost_hmac_request_signature(
            str(request.user.password), method, url, now, {}, body)
        headers['Authorization'] = 'FOST %s:%s' % (
            quote(request.user.username.encode('utf-8')),
            signature)
        headers['X-Fost-Timestamp'] = now
    return headers


def get(url, ttl = 0):
    """Perform a GET request against a Slumber server.
    """
    # Pylint gets confused by the fake HTTP client
    # pylint: disable=E1103
    url_fragment = _use_fake(url)
    if url_fragment:
        file_spec, query = _parse_qs(url_fragment)
        response = _fake.get(file_spec, query,
            HTTP_HOST='localhost:8000', **_sign_request('GET', url))
        if response.status_code in [301, 302]:
            return get(response['location'])
        assert response.status_code == 200, (
            url_fragment, response.status_code)
        content = response.content
    else:
        cache_key = 'slumber.connector.ua.get.%s' % url
        cached = cache.get(cache_key)
        if not cached:
            for _ in range(0, 3):
                response, content = Http().request(
                    url, headers=_sign_request('GET', url))
                if response.status == 200:
                    break
            assert response.status == 200, (url, response.status)
            if ttl:
                cache.set(cache_key, (response, content), ttl)
        else:
            response, content = cached
            response.from_cache = True
    return response, loads(content)


def post(url, data):
    """Perform a POST request against a Slumber server.
    """
    # Pylint gets confused by the fake HTTP client
    # pylint: disable=E1103
    url_fragment = _use_fake(url)
    if url_fragment:
        response = _fake.post(url_fragment, data,
            HTTP_HOST='localhost:8000', **_sign_request('POST', url, data))
        assert response.status_code == 200, \
            (url_fragment, response, response.content)
        content = response.content
    else:
        body = urlencode(data)
        response, content = Http().request(url, "POST", body=body,
            headers = _sign_request('POST', url, data))
        assert response.status == 200, content
    return response, loads(content)

