""" Dispatch type of http accept header handler
"""
from slumber.server.html import build_html as as_html
from slumber.server.json import as_json
from slumber.server.xml import as_xml


def get_handlers_list():
    """The default set of content encoders.
    """
    return [
        ('application/json', as_json),
        ('text/html', as_html),
        ('text/xml', as_xml),
        ('application/xml', as_xml),
    ]


def accept(accept_header, accept_handlers_list=None):
    """Perform the content type negotiation.
    """
    if not accept_handlers_list:
        accept_handlers_list = get_handlers_list()
    for accept_str, fn_handler in accept_handlers_list:
        if accept_str in accept_header:
            return accept_str, fn_handler

    return None, as_json
