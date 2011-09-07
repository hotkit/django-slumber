import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "django_slumber",
    version = "0.4.1.9",
    author = "Kirit Saelensminde",
    author_email = "kirit@felspar.com",
    description = ("RESTful data connector for Django"),
    license = "Boost Software License - Version 1.0 - August 17th, 2003",
    keywords = "django rest data",
    packages = [
        'slumber', 'slumber.connector', 'slumber.operations', 'slumber.server',
        'slumber_test'],
    long_description = read('README.markdown'),
    install_requires = ['simplejson', 'httplib2'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Boost Software License - Version 1.0 - August 17th, 2003",
    ],
)
