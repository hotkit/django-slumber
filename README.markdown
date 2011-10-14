Slumber is a RESTful data connector that can be used to make proper RESTful data services from Django systems.

To install Slumber use:

    pip install  git+git://github.com/KayEss/django-slumber.git

# Using Slumber #

Slumber has two parts, the server and client side. A RESTful service can be used by just adding the server side to an existing Django system. The client side is useful where you want to connect to the data service from another Python system, or even if you just want to decouple the persistence from the user interface layers within Django.

## The Slumber server ##

In order to start to use Slumber on the server side you simply need to include it in your `urls.py` with something like this:

    (r'^slumber/', include('slumber.urls'))

## The Slumber data client ##

The data client is to be found at `slumber.client`. It must be configured to be told the location of the directory server.

    SLUMBER_DIRECTORY='http://localhost:8000/slumber/'

You should also configure a URL prefix for local Slumber accesses. This is set as below in `settings.py`. The value shown below is the default.

    SLUMBER_LOCAL='http://localhost:8000/'

In order to fetch objects from the remote end you should import the client and make use of it:

    from slumber import client

    def do_something():
        pizza = client.slumber_test.Pizza.get(pk=1)
        assert pizza

## Slumber services ##

Services are used when there are multiple RESTful services that all need to communicate together in order to provide a full system. Services are known by name and a single Slumber client can talk to multiple services through the directory server.

All models in a particular Django project can be put into the same service through the use of the SLUMBER_SERVICE setting:

    SLUMBER_SERVICE = 'takeaway'

This will create a takeaway service that all of the models can be found within. Now to access a model from the client the service name also needs to be used:

    shopping_cart = slumber.client.takeaway.order.Cart.get(pk=1)

At least one of the projects must now be designated a Slumber directory and it is configured with the locations of all of the services (i.e. the `takeaway` service running within the same project and the `pizzas` service running on another port on the same development machine):

    SLUMBER_DIRECTORY = {
        'takeaway': 'http://localhost:8000/slumber/takeaway/',
        'pizzas': 'http://localhost:8001/slumber/pizza/',
    }

Note that the directory must list itself!

On the `pizza` service we can now either repeat the exact same directory configuration, or have it point to the directory on the `takeaway` service. I.e. one of the following configurations can be used:

    SLUMBER_DIRECTORY = {
        'takeaway': 'http://localhost:8000/slumber/takeaway/',
        'pizzas': 'http://localhost:8001/slumber/pizza/',
    }

or

    SLUMBER_LOCAL='http://localhost:8000/'

### Using a non Slumber Django project for the directory ###

The Slumber directory doesn't even need to be Django. All that is needed is that the url that the directory points at returns JSON that describes where to find the services. The JSON returned for the above example should look like:

    {
        "services": {
            "takeaway": "http://localhost:8000/slumber/takeaway/",
            "pizzas": "http://localhost:8001/slumber/pizza/"
        }
    }


# Doing development #

_This project uses git flow. Don't forget to do `git flow init`_ (use defaults for all options).

First you will want to create virtual environments to run the tests in. There is a helper script in `test-projects` for this.

    test-projects/make-virtual-environments

In order to use this you will need virtualenv and virtualenv-wrapper.

Once the virtual environments are created the tests can be run using the `runtests` script.

    ./runtests

Note that you do not need to be in a virtual environment when you run this script. It will switch between the required virtual environments automatically when the tests are run.
