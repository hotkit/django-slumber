"""
    Code for the Slumber instance connector.
"""
from urlparse import urljoin

from slumber._caches import CLIENT_INSTANCE_CACHE, \
    MODEL_URL_TO_SLUMBER_MODEL
from slumber.connector.dictobject import DictObject
from slumber.connector.ua import get
from slumber.connector.json import from_json_data


def get_instance(model, instance_url, display_name, **fields):
    """Return an instance of the specified model etc.
    """
    instance_type = type(model.module + '.' + model.name,
        (_InstanceProxy,), {})
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
        self._instance = None

    def __getattr__(self, name):
        """Fetch the underlying instance from the cache if necessary and
        return the attribute value it has.
        """
        if not self._instance:
            # Try to find it in the cache
            self._instance = CLIENT_INSTANCE_CACHE.get(self._url, None)
        if not self._instance:
            # We now have a cache miss so construct a new connector
            self._instance = _InstanceConnector(
                self._url, **self._fields)
            CLIENT_INSTANCE_CACHE[self._url] = self._instance
        return getattr(self._instance, name)

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
        for k, v in json['fields'].items():
            setattr(self, k, from_json_data(self._url, v))
        if name in json['fields'].keys():
            return getattr(self, name)
        return _return_data_array(self._url, json['data_arrays'], self, name)
