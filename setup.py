import os
from setuptools import setup

def read(fname1, fname2):
    if os.path.exists(fname1):
        fname = fname1
    else:
        fname = fname2
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_slumber",
    version = "0.6.6.1",
    author = "Kirit Saelensminde",
    author_email = "kirit@felspar.com",
    url='https://github.com/KayEss/django-slumber',
    description = ("RESTful data connector for Django"),
    long_description = read('README','README.markdown'),
    license = "Boost Software License - Version 1.0 - August 17th, 2003",
    keywords = "django rest data server client",
    packages = [
        'slumber', 'slumber.connector', 'slumber.operations', 'slumber.server',
        'slumber_examples', 'slumber_examples.no_models', 'slumber_examples.tests',
        'slumber_examples.nested1', 'slumber_examples.nested1.nested2',
        'slumber_ex_shop'],
    install_requires = ['simplejson', 'httplib2', 'django-fost-authn >= 0.3.4'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved",
    ],
)
