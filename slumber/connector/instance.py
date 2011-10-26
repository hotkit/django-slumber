"""
    Code for the Slumber instance connector.
"""
from urlparse import urljoin

from slumber._caches import CLIENT_INSTANCE_CACHE, \
    MODEL_URL_TO_SLUMBER_MODEL
from slumber.connector.dictobject import DictObject
from slumber.connector.ua import get
from slumber.connector.json import from_json_data
from slumber.connector.proxies import UserInstanceProxy


INSTANCE_PROXIES = {
        'django/contrib/auth/User/': UserInstanceProxy,
    }


def get_instance(model, instance_url, display_name, **fields):
    """Return an instance of the specified model etc.
    """
    bases = [_InstanceProxy]
    for type_url, proxy in INSTANCE_PROXIES.items():
        # We're going to allow ourselves access to _url within the library
        # pylint: disable = W0212
        if model._url.endswith(type_url):
            bases.append(proxy)
    instance_type = type(model.module + '.' + model.name, tuple(bases), {})
    return instance_type(instance_url, display_name, **fields)


class _InstanceProxy(object):
    """Add an extra layer of indirection between the objects being manipulated
    by the application code and the underlying object. This allows us to
    better handle the cache.
    """
    def __init__(self, url, display, **fields):
        self._url = url
        self._display = display
        self._fields = fields

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


def _return_data_array(base_url, arrays, instance, name):
    """Implement the lazy fetching of the instance data.
    """
    # Pylint makes a bad type deduction
    # pylint: disable=E1103
    if name in arrays.keys():
        data_array = []
        _, data = get(urljoin(base_url, arrays[name]))
        while True:
            for obj in data['page']:
                model_url = urljoin(base_url, obj['type'])
                model = MODEL_URL_TO_SLUMBER_MODEL[model_url]
                instance_url = urljoin(base_url, obj['data'])
                data_array.append(
                    get_instance(model, instance_url, obj['display']))
            if data.has_key('next_page'):
                _, data = get(urljoin(base_url, data['next_page']))
            else:
                break
        setattr(instance, name, data_array)
        return data_array
    else:
        raise AttributeError(name)


class _InstanceConnector(DictObject):
    """Connects to a remote instance.
    """
    def __init__(self, url, **kwargs):
        self._url = url
        super(_InstanceConnector, self).__init__(**kwargs)

    def __getattr__(self, name):
        _, json = get(self._url)
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
                self._url, json['data_arrays'], self, name)

