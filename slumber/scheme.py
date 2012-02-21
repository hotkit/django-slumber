"""
    Utility functions for managing the slumber URL scheme.
"""


def to_slumber_scheme(url, service, services):
    """Look at the URL and convert it to a service based URL if applicable.
    """
    if service and services.has_key(service):
        service_url = services[service]
        if url.startswith(service_url):
            return 'slumber://%s/%s' % (service, url[len(service_url):])
    return url


def from_slumber_scheme(url, service, services):
    """Turn a Slumber URL into a full URI as specified by the service
    configuration.
    """
    if url.startswith('slumber://'):
        if service and services.has_key(service):
            service_prefix = 'slumber://%s/' % service
            if url.startswith(service_prefix):
                service_url = services[service]
                return service_url + url[len(service_prefix):]
        raise NotImplementedError("Service not found")
    return url
