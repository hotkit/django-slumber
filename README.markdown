Slumber is a RESTful data connector that can be used to make proper RESTful data services from Django systems.

To install Slumber use:

    pip install  git+git://github.com/KayEss/django-slumber.git

# Using Slumber #

Slumber has two parts, the server and client side. A RESTful service can be used by just adding the server side to an existing Django system. The client side is useful where you want to connect to the data service from another Python system.

## The Slumber server ##

In order to start to use Slumber on the server side you simply need to include it in your `urls.py` with something like this:

    (r'^slumber/', include('slumber.urls'))

## The Slumber data client ##

The data client is to be found in `sluber.client`. It must be configured to be told the URL prefix for local Slumber accesses. This is set as below in `settings.py`. The value shown below is the default.

    SLUMBER_LOCAL='http://localhost:8000/'


# Doing development #

_This project uses git flow. Don't forget to do `git flow init`_ (use defaults for all options).
