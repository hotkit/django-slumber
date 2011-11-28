"""
    Implements the JSON formatting for both the client and the server.
"""
from urlparse import urljoin


def from_json_data(base_url, json):
    """Convert a JSON representation of some data to the right types within
    the client.
    """
    if json['kind'] == 'object':
        if json['data'] is None:
            return None
        else:
            # It's a remote object
            from slumber.connector.api import get_instance, get_model
            model_url = urljoin(base_url, json['data']['type'])
            data_url = urljoin(base_url, json['data']['data'])
            display = json['data']['display']
            return get_instance(get_model(model_url), data_url, display)
    else:
        return json['data']
