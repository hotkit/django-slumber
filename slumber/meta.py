from django.conf import settings

from slumber.application import DjangoApp


def applications():
    return [get_application(app) for app in settings.INSTALLED_APPS]


def get_application(app_name):
    return DjangoApp(app_name)
