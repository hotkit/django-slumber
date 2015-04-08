from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    (r'^slumber/', include('slumber.urls')),
    (r'^$', 'slumber_examples.views.ok_text'),

    # Examples:
    # url(r'^$', 'django1_7.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
