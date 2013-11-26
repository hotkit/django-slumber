"""
Django settings for django1_6 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wr)!^-y*$(i*@r7ogh0zl9f4g6gmg_d)@$jl*6cgh1()*xo@2d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_nose',

    # Slumber test applications
    'slumber_examples',
    'slumber_examples.nested1',
    'slumber_examples.nested1.nested2',
    'slumber_examples.no_models',

    'slumber_ex_shop',
)
SLUMBER_CLIENT_APPS = ['slumber_examples']

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'fost_authn.Middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_PROFILE_MODULE = 'slumber_examples.Profile'

# Needed to get the Django nose test runner working
TEST_RUNNER='django_nose.NoseTestSuiteRunner'

AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'fost_authn.FostBackend',
    ]

TEMPLATE_DIRS = [
        os.path.join(BASE_DIR, '../../templates'),
    ]

ROOT_URLCONF = 'django1_6.urls'

WSGI_APPLICATION = 'django1_6.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
