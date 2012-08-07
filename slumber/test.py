"""
    A test version of the client.
"""
import mock

from slumber.connector.api import get_instance, get_model_type
from slumber.connector.dictobject import DictObject


class _Operations(object):
    """Allows us to fetch URLs for operations in mocks reliably.
    """
    def __init__(self, url):
        self._url = 'http://' + url
        self._suffix = '/'

    def __getitem__(self, name):
        return self._url + name + self._suffix


class _MockModel(object):
    """A mock model object type so we can attach things more sanely for
    mocking purposes.
    """
    def __init__(self, client, url, instance_type):
        self.client = client
        self._url = url
        self._operations = _Operations(url)
        self.instance_type = instance_type
        self.instances = []

    def __call__(self, url, display_name):
        return get_instance('slumber://' + self._url, url, display_name)

    def get(self, **query):
        """Implements a mocked version of the get operator.
        """
        for i in self.instances:
            found = True
            for k, v in query.items():
                found = found and hasattr(i, k) and (
                    getattr(i, k) == v or unicode(getattr(i, k)) == unicode(v))
            if found:
                if hasattr(i, '_url'):
                    return get_instance(
                        'slumber://' + self._url, i._url, None)
                else:
                    return i
        assert False, "The instance was not found\n%s" % query

    def create(self, **items):
        """Implements a mocked version of the create operator.
        """
        instance = self.instance_type(self._url, **items)
        self.instances.append(instance)
        self.client._instances.append(instance)
        return instance
        
    def update(self, instance_connector, **updating_data):
        """ Implement a mocked version of update operator """
        updating_id = instance_connector.pk

        for instance in self.instances:
            if instance.pk == updating_id:
                for key, value in updating_data.items():
                    setattr(instance, key, value)


class _MockInstance(DictObject):
    """A mock instance that will add in a _url parameter.
    """
    def __init__(self, model_url, **kwargs):
        super(_MockInstance, self).__init__(**kwargs)
        self._operations = _Operations(model_url)
        if hasattr(self, 'pk') or hasattr(self, 'id'):
            pk = getattr(self, 'pk', getattr(self, 'id', None))
            self._operations._suffix = '/%s/' % pk
            self._url = ('slumber://' + model_url +
                'data%s' % self._operations._suffix)

    def __repr__(self):
        return getattr(self, '_url', 'Unknown mock instance')


class _MockClient(DictObject):
    """Mock slumber client class.
    """
    def __init__(self, **instances):
        super(_MockClient, self).__init__()
        self._instances = []
        for model, instances in instances.items():
            root = self
            for k in model.split('__')[:-1]:
                if not hasattr(root, k):
                    setattr(root, k, DictObject())
                root = getattr(root, k)
            model_name = model.split('__')[-1]
            model_url = model.replace('__', '/') + '/'
            model_type = get_model_type(model_url, [_MockModel])
            instance_type = type(model_url, (_MockInstance,), {})
            mock_model = model_type(self, model_url, instance_type)
            setattr(root, model_name, mock_model)
            for instance in instances:
                mock_model.create(**instance)

    def _flush_client_instance_cache(self):
        """Empty stub so that the middleware works in tests.
        """


def mock_client(**instances):
    """Replaces the client with a mocked client that provides access to the
    provided applications, models and instances.
    """
    models = _MockClient(**instances)
    def decorator(test_method):
        """The actual decorator that is going to be used on the test method.
        """
        @mock.patch('slumber._client', models)
        def test_wrapped(test, *a, **kw):
            """The wrapper for the test method.
            """
            test_method(test, *a, **kw)
        test_wrapped.__doc__ = test_method.__doc__
        return test_wrapped
    return decorator


def mock_ua(test_method):
    """Allow the user agent to set up expectations.
    """
    class MockUA(object):
        """Records the expectations and check that they are met properly.
        """
        def __init__(self, test):
            self.expectations = []
            self.test = test

        def get(self, url, data):
            """Record a get expectation.
            """
            self.expectations.append(('get', url, None, data))

        def post(self, url, edata, rdata):
            """Record a post expectation.
            """
            self.expectations.append(('post', url, edata, rdata))

        def do_get(self, url, _ttl = 0, _codes = None):
            """The patch for the user agent get.
            """
            self.test.assertTrue(self.expectations,
                "No expectation for GET %s" % url)
            emethod, eurl, edata, rdata = self.expectations.pop(0)
            self.test.assertEqual(emethod, 'get')
            self.test.assertEqual(url, eurl)
            self.test.assertIsNone(edata)
            return None, rdata

        def do_post(self, url, data, _codes = None):
            """The patch for the user agent post.
            """
            self.test.assertTrue(self.expectations,
                "No expectation for POST %s\n%s" % (url, data))
            emethod, eurl, edata, rdata = self.expectations.pop(0)
            self.test.assertEqual(emethod, 'post')
            self.test.assertEqual(url, eurl)
            self.test.assertEqual(data, edata)
            return None, rdata

    def test_wrapped(test, *a, **kw):
        """Test decorator that patches the user agent and ensures all
        expectations are met.
        """
        user_agent = MockUA(test)
        with mock.patch('slumber.connector.ua._get', user_agent.do_get):
            with mock.patch('slumber.connector.ua._post', user_agent.do_post):
                test_method(test, user_agent, *a, **kw)
                test.assertEqual(user_agent.expectations, [],
                    "There are un-used expectations")
    test_wrapped.__doc__ = test_method.__doc__
    return test_wrapped

