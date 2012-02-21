"""
    Utility functions for managing the slumber URL scheme.
"""


def to_slumber_scheme(url, service, services):
    """Look at the URL and convert it to a service based URL if applicable.
    """
    if services.has_key(service):
        service_url = services[service]
        if url.startswith(service_url):
            return 'slumber://%s/%s' % (service, url[len(service_url):])
    return url
