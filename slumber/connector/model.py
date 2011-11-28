"""
    Code for the Slumber model connector.
"""
from urllib import urlencode
from urlparse import urljoin, urlparse

from slumber._caches import MODEL_URL_TO_SLUMBER_MODEL
from slumber.connector.dictobject import DictObject
from slumber.connector.instance import get_instance
from slumber.connector.json import from_json_data
from slumber.connector.proxies import UserModelProxy
from slumber.connector.ua import get


def _ensure_absolute(url):
    """Assert that a given URL is absolute.
    """
    assert urlparse(url)[0], "The URL <> must be absolute" % url


MODEL_PROXIES = {
        'django/contrib/auth/User/': UserModelProxy,
    }


def get_model(url):
    """Return the client model connector for a given URL.
    """
    _ensure_absolute(url)
    if not MODEL_URL_TO_SLUMBER_MODEL.has_key(url):
        bases = [ModelConnector]
        for type_url, proxy in MODEL_PROXIES.items():
            if url.endswith(type_url):
                bases.append(proxy)
        model_type = type(url, tuple(bases), {})
        return model_type(url)
    else:
        return MODEL_URL_TO_SLUMBER_MODEL[url]


class ModelConnector(DictObject):
    """Handles the connection to a Django model.
    """
    def __init__(self, url, **kwargs):
        _ensure_absolute(url)
        assert not MODEL_URL_TO_SLUMBER_MODEL.has_key(url), \
            (url, MODEL_URL_TO_SLUMBER_MODEL.keys())
        MODEL_URL_TO_SLUMBER_MODEL[url] = self
        self._url = url
        super(ModelConnector, self).__init__(**kwargs)

    def __call__(self, url, display_name):
        """Construct an instance of this model.
        """
        return get_instance(self, url, display_name)

    def __getattr__(self, name):
        attrs = ['name', 'module']
        if name in attrs + ['_operations']:
            _, json = get(self._url)
            # We need to set this outside of __init__ for it to work correctly
            # pylint: disable = W0201
            self._operations = dict([(o, urljoin(self._url, u))
                for o, u in json['operations'].items()])
            for attr in attrs:
                setattr(self, attr, json[attr])
            return getattr(self, name)
        else:
            raise AttributeError(name)

    def get(self, **kwargs):
        """Implements the client side for the model 'get' operator.
        """
        assert len(kwargs), \
            "You must supply kwargs to filter on to fetch the instance"
        url = urljoin(self._url, 'get/')
        _, json = get(url + '?' + urlencode(kwargs))
        return get_instance(self,
            urljoin(self._url, json['identity']), json['display'],
            **dict([(k, from_json_data(self._url, j))
                for k, j in json['fields'].items()]))
