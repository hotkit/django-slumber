from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^slumber/', include('slumber.urls')),
    url(r'^$', 'slumber_examples.views.ok_text'),

    url(r'^admin/', include(admin.site.urls)),
]
