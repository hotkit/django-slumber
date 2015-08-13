from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'slumber_examples.views.ok_text'),
    url(r'^slumber/', include('slumber.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
