""" Dispatch type of http accept header handler
"""

from slumber.server.default_accept_handler import default_handler
from slumber.server.xml import as_xml
from slumber.server.html import build_html as as_html


def get_handlers_list():
    return [
        ('application/xml', as_xml),
        ('text/html', as_html)
    ]


def accept(request_meta_data, accept_handlers_list=None):
    if not accept_handlers_list:
        accept_handlers_list = get_handlers_list()
    for accept_str, fn_handler in accept_handlers_list:
        if accept_str in request_meta_data:
            return fn_handler
    else:
        return default_handler
