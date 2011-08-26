"""
    Code for the Slumber model connector.
"""
from urllib import urlencode
from urlparse import urljoin

from slumber._caches import MODEL_URL_TO_SLUMBER_MODEL
from slumber.connector.dictobject import DictObject
from slumber.connector.instance import get_instance
from slumber.connector.ua import get
from slumber.json import from_json_data


class ModelConnector(DictObject):
    """Handles the connection to a Django model.
    """
    def __init__(self, url, **kwargs):
        assert not MODEL_URL_TO_SLUMBER_MODEL.has_key(url), \
            (url, MODEL_URL_TO_SLUMBER_MODEL.keys())
        MODEL_URL_TO_SLUMBER_MODEL[url] = self
        self._url = url
        super(ModelConnector, self).__init__(**kwargs)

    def __getattr__(self, name):
        attrs = ['name', 'module']
        if name in attrs:
            _, json = get(self._url)
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
