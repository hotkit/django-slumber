""" Dispatch type of http accept header handler
"""

from slumber.server.default_accept_handler import default_handler
from slumber.server.html import build_html as as_html
from slumber.server.xml import as_xml


def get_handlers_list():
    """The default set of content encoders.
    """
    return [
        ('text/html', as_html),
        ('application/xml', as_xml),
    ]


def accept(request_meta_data, accept_handlers_list=None):
    """Perform the content type negotiation.
    """
    if not accept_handlers_list:
        accept_handlers_list = get_handlers_list()
    for accept_str, fn_handler in accept_handlers_list:
        if accept_str in request_meta_data:
            return fn_handler
    return default_handler

