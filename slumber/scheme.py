"""
    Utility functions for managing the slumber URL scheme.
"""


class SlumberServiceURLError(Exception):
    """This exception is thrown if the Slumber URL has a service that does
    not match the service that it should have.
    """
    pass


def to_slumber_scheme(url, service, services):
    """Look at the URL and convert it to a service based URL if applicable.
    """
    if service and services and services.has_key(service):
        service_url = services[service]
        if url.startswith(service_url):
            return 'slumber://%s/%s' % (service, url[len(service_url):])
    return url


def from_slumber_scheme(url, service, services):
    """Turn a Slumber URL into a full URI as specified by the service
    configuration.
    """
    if url.startswith('slumber://'):
        if not services:
            raise SlumberServiceURLError(
                "There are no services in the Slumber directory "
                "so the URL %s for service '%s' cannot be dereferenced"
                    % (url, service))
        if service and services.has_key(service):
            service_prefix = 'slumber://%s/' % service
            if url.startswith(service_prefix):
                service_url = services[service]
                return service_url + url[len(service_prefix):]
        raise SlumberServiceURLError(
            "Service in URL %s does not match requested service '%s'"
                % (url, service))
    return url
