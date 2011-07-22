Slumber is a RESTful data connector that can be used to make proper RESTful data services from Django systems.

# Using Slumber #

Slumber has two parts, the server and client side. A RESTful service can be used by just adding the server side to an existing Django system. The client side is useful where you want to connect to the data service from another Python system.

## The Slumber server ##

In order to start to use Slumber on the server side you simply need to include it in your `urls.py` with something like this:

    (r'^slumber/', include('slumber.urls'))

## The Slumber data client ##

This part of Slumber has not yet been written, so there is no data connector yet :(


# Doing development #

_This project uses git flow. Don't forget to do `git flow init`_ (use defaults for all options).
