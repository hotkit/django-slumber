# -*- coding: utf-8 -*-
"""
    The Django URLs for the server.
"""
try:
    # This API has changed.
    # pylint: disable=no-name-in-module
    from django.conf.urls import patterns
except ImportError:
    from django.conf.urls.defaults import patterns


# The name urlpatterns is defined by Django and we can't change it
# pylint: disable=C0103
#urlpatterns = patterns('', *_urls.items())
urlpatterns = patterns('',
    ('.*', 'slumber.server.views.service_root'))
