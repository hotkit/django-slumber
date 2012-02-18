"""
    Allow us to get an instance directly from the JSON data for an object.
"""
from urllib import urlencode
from urlparse import urljoin, urlparse

from slumber._caches import CLIENT_INSTANCE_CACHE, \
    MODEL_URL_TO_SLUMBER_MODEL
from slumber.connector.configuration import INSTANCE_PROXIES, MODEL_PROXIES
from slumber.connector.dictobject import DictObject
from slumber.connector.json import from_json_data
from slumber.connector.ua import get, post


def _ensure_absolute(url):
    """Assert that a given URL is absolute.
    """
    assert urlparse(url)[0], "The URL <%s> must be absolute" % url


def get_instance(model, instance_url, display_name, fields = None):
    """Return an instance of the specified model etc.
    """
    fields = fields or {}
    bases = [_InstanceProxy]
    for type_url, proxy in INSTANCE_PROXIES.items():
        # We're going to allow ourselves access to _url within the library
        # pylint: disable = W0212
        if model._url.endswith(type_url):
            bases.append(proxy)
    type_name = str(model.module + '.' + model.name)
    instance_type = type(type_name, tuple(bases), {})
    return instance_type(instance_url, display_name, fields)


def get_model(url):
    """Return the client model connector for a given URL.
    """
    if not MODEL_URL_TO_SLUMBER_MODEL.has_key(url):
        bases = [ModelConnector]
        for type_url, proxy in MODEL_PROXIES.items():
            if url.endswith(type_url):
                bases.append(proxy)
        model_type = type(str(url), tuple(bases), {})
        return model_type(url)
    else:
        return MODEL_URL_TO_SLUMBER_MODEL[url]


def get_instance_from_data(base_url, json):
    """Return a local instance proxy for the object described by the provided
    JSON like Python datastructure.
    """
    model = get_model(urljoin(base_url, json['type']))
    instance_url = urljoin(base_url, json['operations']['data'])
    return get_instance(model, instance_url, json['display'],
        dict([(k, from_json_data(base_url, j))
            for k, j in json['fields'].items()]))


class ModelConnector(DictObject):
    """Handles the connection to a Django model.
    """
    _CACHE_TTL = 0

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
            _, json = get(self._url, self._CACHE_TTL)
            # We need to set this outside of __init__ for it to work correctly
            # pylint: disable = W0201
            self._operations = dict([(o, urljoin(self._url, u))
                for o, u in json['operations'].items()])
            for attr in attrs:
                setattr(self, attr, json[attr])
            return getattr(self, name)
        else:
            raise AttributeError(name)

    def create(self, **kwargs):
        """Implements the client side for the model `create` operator.
        """
        url = urljoin(self._url, self._operations['create'])
        _, json = post(url, kwargs)
        return get_instance_from_data(url, json)

    def get(self, **kwargs):
        """Implements the client side for the model 'get' operator.
        """
        assert len(kwargs), \
            "You must supply kwargs to filter on to fetch the instance"
        url = urljoin(self._url, 'get/')
        _, json = get(url + '?' + urlencode(kwargs), self._CACHE_TTL)
        return get_instance_from_data(url, json)


class _InstanceProxy(object):
    """Add an extra layer of indirection between the objects being manipulated
    by the application code and the underlying object. This allows us to
    better handle the cache.
    """
    def __init__(self, url, display, fields = None):
        super(_InstanceProxy, self).__init__()
        self._url = url
        self._display = display
        self._fields = fields or {}

    def _fetch_instance(self):
        """Fetch the underlying instance.
        """
        instance = CLIENT_INSTANCE_CACHE.get(self._url, None)
        if not instance:
            # We now have a cache miss so construct a new connector
            instance = _InstanceConnector(self._url, **self._fields)
            if CLIENT_INSTANCE_CACHE.enabled:
                CLIENT_INSTANCE_CACHE[self._url] = instance
        return instance

    def __getattr__(self, name):
        """Fetch the underlying instance from the cache if necessary and
        return the attribute value it has.
        """
        return getattr(self._fetch_instance(), name)

    def __setattr__(self, name, value):
        """Write the attribute through to the underlying instance.
        """
        if name.startswith('_'):
            return super(_InstanceProxy, self).__setattr__(name, value)
        return setattr(self._fetch_instance(), name, value)

    def __unicode__(self):
        """Allow us to take the unicode name of the instance
        """
        return self._display


def _return_data_array(base_url, arrays, instance, name, cache_ttl):
    """Implement the lazy fetching of the instance data.
    """
    # Pylint makes a bad type deduction
    # pylint: disable=E1103
    if name in arrays.keys():
        data_array = []
        _, data = get(urljoin(base_url, arrays[name]), cache_ttl)
        while True:
            for obj in data['page']:
                model_url = urljoin(base_url, obj['type'])
                model = MODEL_URL_TO_SLUMBER_MODEL[model_url]
                instance_url = urljoin(base_url, obj['data'])
                data_array.append(
                    get_instance(model, instance_url, obj['display']))
            if data.has_key('next_page'):
                _, data = get(urljoin(base_url, data['next_page']), cache_ttl)
            else:
                break
        setattr(instance, name, data_array)
        return data_array
    else:
        raise AttributeError(name)


class _InstanceConnector(DictObject):
    """Connects to a remote instance.
    """
    _CACHE_TTL = 0

    def __init__(self, url, **kwargs):
        self._url = url
        super(_InstanceConnector, self).__init__(**kwargs)

    def __getattr__(self, name):
        _, json = get(self._url, self._CACHE_TTL)
        # We need to set this outside of __init__ for it to work correctly
        # pylint: disable = W0201
        self._operations = dict([(o, urljoin(self._url, u))
            for o, u in json['operations'].items()])
        for k, v in json['fields'].items():
            setattr(self, k, from_json_data(self._url, v))
        if name in json['fields'].keys():
            return getattr(self, name)
        elif name == '_operations':
            return self._operations
        else:
            return _return_data_array(
                self._url, json['data_arrays'], self, name, self._CACHE_TTL)


# This is at the end to ensure that the built in proxies are loaded up properly
# We also don't care that the import is unused
# pylint: disable = W0611
import slumber.connector.proxies

