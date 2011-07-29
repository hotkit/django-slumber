# -*- coding: utf-8 -*-
"""
    The Django URLs for the server.
"""
from django.conf.urls.defaults import patterns

from slumber.http import view_handler
from slumber.meta import applications


_urls = {'^$': 'slumber.views.get_applications'}

for app in applications():
    _urls['^(%s)/$' % app.path] = 'slumber.views.get_models'
    for model in app.models.values():
        _urls['^(%s)/(%s)/$' % (app.path, model.name)] = \
            'slumber.views.get_model'
        for op in model.operations():
            _urls['^(%s)/(%s)/%s/%s$' %
                    (app.path, model.name, op.name, op.regex)] = \
                view_handler(op.operation)

# The name urlpatterns is defined by Django and we can't change it
# pylint: disable=C0103
urlpatterns = patterns('', *_urls.items())
