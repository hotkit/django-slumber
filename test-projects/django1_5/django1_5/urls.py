from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^slumber/', include('slumber.urls')),

    (r'^$', 'slumber_examples.views.ok_text'),

    # Examples:
    # url(r'^$', 'django1_5.views.home', name='home'),
    # url(r'^django1_5/', include('django1_5.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
