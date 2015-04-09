# -*- coding: utf-8 -*-
"""
    The Django URLs for the server.
"""
try:
    # This API has changed.
    # pylint: disable=no-name-in-module
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url


# The name urlpatterns is defined by Django and we can't change it
# pylint: disable=C0103
urlpatterns = [
    url('.*', 'slumber.server.views.service_root')
]
