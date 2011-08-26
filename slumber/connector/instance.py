"""
    Code for the Slumber instance connector.
"""
from urlparse import urljoin

from slumber.connector.dictobject import DictObject
from slumber.connector.ua import get
from slumber.json import from_json_data


def get_instance(model, instance_url, display_name, **fields):
    """Return an instance of the specified model etc.
    """
    instance_type = type(model.module + '.' + model.name,
        (_InstanceConnector,), {})
    obj = instance_type(
        instance_url, display_name,
        **fields)
    return obj


def _return_data_array(base_url, arrays, _, name):
    """Implement the lazy fetching of the instance data.
    """
    # Pylint makes a bad type deduction
    # pylint: disable=E1103
    if name in arrays.keys():
        data_array = []
        _, data = get(urljoin(base_url, arrays[name]))
        while True:
            for obj in data['page']:
                data_array.append(
                    _InstanceConnector(
                        urljoin(base_url, obj['data']), obj['display']))
            if data.has_key('next_page'):
                _, data = get(urljoin(base_url, data['next_page']))
            else:
                break
        return data_array
    else:
        raise AttributeError(name)


class _InstanceConnector(DictObject):
    """Connects to a remote instance.
    """
    def __init__(self, url, display, **kwargs):
        self._url = url
        self._unicode = display
        super(_InstanceConnector, self).__init__(**kwargs)

    def __unicode__(self):
        return self._unicode

    def __getattr__(self, name):
        _, json = get(self._url)
        for k, v in json['fields'].items():
            setattr(self, k, from_json_data(self._url, v))
        if name in json['fields'].keys():
            return getattr(self, name)
        return _return_data_array(self._url, json['data_arrays'], self, name)
