"""
Django settings for web_omics project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os

from configurations import Configuration, values
from django.contrib.messages import constants as message_constants
from django.urls import reverse_lazy

import logging
import sys


def getString(name, default):
    if name not in os.environ:
        return default
    return os.environ[name]

CACHE_DURATION = int(getString('CACHE_DURATION', '604800')) # defaults to a week in seconds


class Common(Configuration):


    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = values.BooleanValue(False)

    ALLOWED_HOSTS = []

    #Trying to set up email contact for the website
    SENDGRID_API_KEY = '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'

    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'whitenoise.runserver_nostatic',
        'django.contrib.staticfiles',
        'django_extensions',
        'django_select2',
        'webpack_loader',
        'web_omics.users',
        'registration',
        'rest_framework',
        'met_explore',
    ]

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        # If an env_variable is not set use 'INFO' - set in PyCharm run configurations
        'root': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'handlers': ['console']
        }
    }


    WEBPACK_LOADER = {
        'DEFAULT': {
            'BUNDLE_DIR_NAME': 'bundles/',
            'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        }
    }

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'web_omics.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'web_omics.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/2.0/ref/settings/#databases
    DATABASES = values.DatabaseURLValue(
        'sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    )

    # Password validation
    # https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/
    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = '/static/'
    STATIC_PATH = os.path.join(BASE_DIR,'static')
    STATIC_ROOT = os.path.join(BASE_DIR,'assets')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    STATICFILES_DIRS = (
        STATIC_PATH,
    )


    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(BASE_DIR,'django_cache'),
            'TIMEOUT': CACHE_DURATION
        }
    }

    # For file upload
    # See https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    AUTH_USER_MODEL = 'users.User'
    LOGIN_URL = reverse_lazy('login')

class Development(Common):
    """
    The in-development settings and the default configuration.
    """
    DEBUG = True
    MESSAGE_LEVEL = message_constants.DEBUG

    ALLOWED_HOSTS = ['*']

    INTERNAL_IPS = [
        '127.0.0.1'
    ]

    MIDDLEWARE = Common.MIDDLEWARE + [
        # 'debug_toolbar.middleware.DebugToolbarMiddleware'
    ]

    # turn this on to enable SQL logging from django
    # works when DEBUG = True, also remember to set the log level to DEBUG
    # LOGGING = {
    #     'version': 1,
    #     'filters': {
    #         'require_debug_true': {
    #             '()': 'django.utils.log.RequireDebugTrue',
    #         }
    #     },
    #     'handlers': {
    #         'console': {
    #             'level': 'DEBUG',
    #             'filters': ['require_debug_true'],
    #             'class': 'logging.StreamHandler',
    #         }
    #     },
    #     'loggers': {
    #         'django.db.backends': {
    #             'level': 'DEBUG',
    #             'handlers': ['console'],
    #         }
    #     }
    # }


class Staging(Common):
    """
    The in-staging settings.
    """
    # Security
    SESSION_COOKIE_SECURE = values.BooleanValue(True)
    SECURE_BROWSER_XSS_FILTER = values.BooleanValue(True)
    SECURE_CONTENT_TYPE_NOSNIFF = values.BooleanValue(True)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = values.BooleanValue(True)
    SECURE_HSTS_SECONDS = values.IntegerValue(31536000)
    SECURE_REDIRECT_EXEMPT = values.ListValue([])
    SECURE_SSL_HOST = values.Value(None)
    SECURE_SSL_REDIRECT = values.BooleanValue(True)
    SECURE_PROXY_SSL_HEADER = values.TupleValue(
        ('HTTP_X_FORWARDED_PROTO', 'https')
    )

class Dev(Configuration):
    DEBUG = True


class Production(Staging):
    """
    The in-production settings.
    """
    pass
