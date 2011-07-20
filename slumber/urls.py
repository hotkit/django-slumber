# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns

from slumber.http import view_handler
from slumber.meta import applications


urls = {'^$': 'slumber.views.get_applications'}

for app in applications():
    urls['^(%s)/$' % app.path] = 'slumber.views.get_models'
    for model in app.models.values():
        urls['^(%s)/(%s)/$' % (app.path, model.name)] = 'slumber.views.get_model'
        for op in model.operations():
            urls['^(%s)/(%s)/%s/%s$' % (app.path, model.name, op.name, op.regex)] \
                = view_handler(op.operation)

urlpatterns = patterns('', *urls.items())
