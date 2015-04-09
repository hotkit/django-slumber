from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^slumber/', include('slumber.urls')),
    url(r'^$', 'slumber_examples.views.ok_text'),

    # Examples:
    # url(r'^$', 'django1_7.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
