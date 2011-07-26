from django.conf import settings
from django.test.client import Client as FakeClient

from httplib2 import Http
from simplejson import loads


_fake = FakeClient()
_http = Http()


def get(url, query={}):
    slumber_local = getattr(settings, 'SLUMBER_LOCAL', 'http://localhost:8000/')
    if url.startswith(slumber_local):
        url_fragment = url[len(slumber_local) - 1:]
        response = _fake.get(url_fragment, query,
            HTTP_HOST='localhost:8000')
        if response.status_code in [301, 302]:
            return get(response['location'])
        assert response.status_code == 200, (url_fragment, response)
        content = response.content
    else:
        assert not query # Not implemented for remote end yet
        response, content = _http.request(url)
        assert response.status == 200, url
    return response, loads(content)
