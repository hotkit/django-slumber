Slumber is a RESTful data connector that can be used to make proper RESTful data services from Django systems.

To install Slumber use:

    pip install django_slumber

To install the current development version use:

    pip install  git+git://github.com/KayEss/django-slumber.git@develop


# Using Slumber #

Slumber has two parts, the server and client side. A RESTful service can be used by just adding the server side to an existing Django system. The client side is useful where you want to connect to the data service from another Python system, or even if you just want to decouple the persistence from the user interface layers within Django.

## The Slumber server ##

In order to start to use Slumber on the server side you simply need to include it in your `urls.py` with something like this:

    (r'^slumber/', include('slumber.urls'))

Note that slumber will not accept any anonymous requests. These will always result in 401 responses. The simplest to configure option is to make use of local IP based authentication. This is not recommended for production use, but is useful for development.

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

### The RemoteForeignKey model field ###

The `RemoteForeignKey` model field is used where you want a foreign key that points to an object on a different data service.

#### `model_url` ####

Controls whether Slumber will re-write URLs saved in the database to be relative to the service that it is given. If the URL starts with the same string as the URL for the specified service then Slumber will replace that prefix with `slumber://service/` before putting the data into the database and replace that with the service prefix when reading the data from the database. This means that if you copy a database, for example, from production to testing all of the URLs will come out against the correct services on the test server.

The model URL may be specified in the `slumber:` form so that the real URL will be calculated depending on the deployment configuration.

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

Note that the directory must list itself. Even more important is that this is an absolute URL!

On the `pizza` service we can now either repeat the exact same directory configuration, or have it point to the directory on the `takeaway` service. I.e. one of the following configurations can be used:

    SLUMBER_DIRECTORY = {
        'takeaway': 'http://localhost:8000/slumber/takeaway/',
        'pizzas': 'http://localhost:8001/slumber/pizza/',
    }

or

    SLUMBER_DIRECTORY = 'http://localhost:8000/slumber/'


### Django application services ###

Sometimes it's useful to be able to put a Django application into a service. There's a few ways of doing this. If it's a single application that needs to be in a service then the application name can be given as the location of a service in the `SLUMBER_DIRECTORY`. For example:

    SLUMBER_DIRECTORY = {
        'auth': 'django.contrib.auth',
        'pizzas': 'slumber_examples',
    }

For this to work the application name given in the service configuration must exactly match the name that is in Django's `INSTALLED_APPS` setting. When used in this way the service will point directly to the Django application mentioned.

''NB'' The current implementation aliases the application to where it is exposed on the main service. This does expose the requested application, but fails to remove the application from the main service applications. I.e. on the above example, both `auth` and `pizzas` will have all django.contrib.auth application exposed through the client.


### Using a non Slumber Django project for the directory ###

The Slumber directory doesn't even need to be Django. All that is needed is that the url that the directory points at returns JSON that describes where to find the services. The JSON returned for the above example should look like:

    {
        "services": {
            "takeaway": "http://localhost:8000/slumber/takeaway/",
            "pizzas": "http://localhost:8001/slumber/pizza/"
        }
    }


## Slumber operations ##

Slumber contains a number of default REST end points on the server side (called operations) which also have a client implementation (called a proxy). Slumber will expose the applications and the models that you have in your Django project and currently provides operations at both the model and instance level.

When dealing with operations that create and modify data it's important to remember that each operation will run in its own transaction on the server and cannot be rolled back once done.

### create (model) ###

Creates a new instance of the model type on the slumber server. In order to use this the user must have the standard `app.add_model` permission.

### delete (instance) ###

Uses a POST request to delete the instance. The user requires the `app.delete_model` permission.

### data (instance) ###

Returns the instance attributes and provides links to related data. Only authenticated users may get instance data.

#### Customising Slumber data ####

When Slumber loads the applications you have defined in your `settings.py` it will also try to load a module called `slumber_conf` from the same place as your models. This can be used to customise how models appear on the Slumber server.

    from models import Shop
    from slumber import configure

    configure(Shop,
        properties_ro = ['web_site'])

This will make a new read-only property `web_site` available in the data about instances populated from the `web_site` property on that model.

### update (instance) ###

Allows the instance attributes to be changed. The user must have the `app.change_model` permission.


## Customising Slumber operations ##

New operations can be added to a model through the configure call. This should be placed in your `slumber_config` file (in `slumber_config.py` in your application folder).

    from slumber import configure

    configure(Pizza,
        operations_extra = [(OrderPizza, 'order')])

You need to a pass a list of binary tuples which contain the operation implementation and the name of the operation.


## Customising the Slumber client ##

Operations that you wish to expose on the client side can be added to a proxy that implements the binding in any way you choose. Proxies come in two types: model proxies and instance proxies.

When the client creates a model instance to connect to a remote model it will look for a user defined proxy class and use that as a mix-in super class for the model type it builds. This allows you to place methods on the proxy and have them used by your client code.

    class ShopProxy(object):
        def has_shop_proxy(self):
            return True

This proxy can be set up by configuring it in your `slumber_config.py` file:

    configure('/slumber_examples/Shop/',
        model_proxy = ShopProxy)

For the model URL we need to specify enough of the model URL that it will be unique. Normally just the application and model name are needed, but sometimes you will want to include service names if you want to have the same model use different proxies depending on the service it's connected to.

Note that although this is a model proxy the method on the proxy is still an instance method and not a class method or static.

Instance proxies are done in exactly the same way, but the configuration is done via `instance_proxy` instead.

    class PizzaProxy(object):
        def has_pizza_proxy(self):
            return True

And:

    configure('/slumber_examples/Pizza/',
        instance_proxy = PizzaProxy)

If your proxy needs to find an operation URL then they will appear in `self._operations`, which is a dict keyed on the operation name given on the server.

    from slumber.connector.ua import get

    def Example(object):
        def proxy_operation(self):
            json = get(self._operations['operation-name']

This would expect to find an operation name `operation-name` on the server and will issue a GET against it.


## Slumber remote authentication and authorization ##

Slumber is also able to help you manage centralised authentication and authorization across RESTful services. This allows you to make use of `django.contrib.auth` on one service to handle permissions on another.

In order to make use of remote authentication you will need to add an authentication backend. The default Django settings don't include `AUTHENTICATION_BACKENDS` so you will need to add this. Typically you will want to turn off Django's normal authentication back end.

    AUTHENTICATION_BACKENDS = [
        'slumber.connector.authentication.Backend',
    ]

Any server can be used as the central store, but to get Slumber to make use of it Slumber must be properly configured. Continuing our pizza example from earlier and assuming that we have a Slumber server exposed at `http://auth.example.com/slumber/` we would configure our pizza service as follows.

    SLUMBER_SERVICE = 'pizzas'
    SLUMBER_DIRECTORY = {
        'auth': 'http://auth.example.com/slumber/',
        'pizzas': 'http://localhost:8000/'
    }

Note that the service based configuration must be used and there must be an `auth` service. The `auth` service is allowed to be an alias onto another location. For example, if we had an `accounting` service that was to handle authentication and authorization then we could configure it using:

    SLUMBER_SERVICE = 'accounting'

To use this as the `auth` service from elsewhere we would now need to give the accounting URL as the `auth` location to other services. I.e.:

    SLUMBER_DIRECTORY = {
        'auth': 'http://accounting.example.com/slumber/accounting/',
        'accounting': 'http://accounting.example.com/slumber/accounting/',
        'pizzas': 'http://localhost:8000/'
    }


## Caching of requests ##

Slumber includes some simple HTTP request caching within the client connector. By default this caching is turned off for all models. It can be enabled on a per model basis by adding proxies for the models and in the instances and including a `_CACHE_TTL` attribute. This will cache the GET responses for the number of seconds specified in the time-to-live.

If you include your own GET requests to the user agent in a proxy then you should remember to pass the cache TTL value:

    ua.get(url, self._CACHE_TTL)

See the file `slumber/connector/proxies.py` for examples on the User object.


# Doing development #

_This project uses git flow. Don't forget to do `git flow init -d`_ (i.e. use defaults for all options).

First you will want to create virtual environments to run the tests in. There is a helper script in `test-projects` for this.

    test-projects/make-virtual-environments

In order to use this you will need virtualenv and virtualenv-wrapper.

Once the virtual environments are created the tests can be run using the `runtests` script.

    ./runtests

Note that you do not need to be in a virtual environment when you run this script. It will switch between the required virtual environments automatically when the tests are run.
