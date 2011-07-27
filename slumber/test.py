

def mock_client(**instances):
    def decorator(test_method):
        def wrapped(test):
            test_method(test)
        return wrapped
    return decorator
