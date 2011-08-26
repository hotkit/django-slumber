"""
    Code for the Slumber client connector.
"""
from urllib import urlencode
from urlparse import urljoin

from slumber.connector.dictobject import DictObject, LazyDictObject
from slumber.connector.instance import _return_data_array
from slumber.connector.ua import get
from slumber.json import from_json_data


class ModelConnector(DictObject):
    """Handles the connection to a Django model.
    """
    def __init__(self, url, **kwargs):
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
        def get_data_array(obj, name):
            """Implement simple partial application using a closure.
            """
            return _return_data_array(self._url, json['data_arrays'], obj, name)
        instance_type = type(self.module + '.' + self.name,
            (LazyDictObject,), {})
        obj = instance_type(get_data_array,
            **dict([(k, from_json_data(self._url, j))
                for k, j in json['fields'].items()]))
        return obj
