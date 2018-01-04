"""
Django settings for avicrypto project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from urllib2 import urlparse
# import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q+@$$hpdjv$l-g9x7pz55_5#@fq29s@!25#r@_&$1_@l^j4-2z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'addons.accounts',
    'addons.packages',
    'addons.transactions',
    'addons.wallet',
]

# MIDDLEWARE_CLASSES = (
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    # 'whitenoise.middleware.WhiteNoiseMiddleware')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'avicrypto.urls'

TEMPLATES = [
    # {
    #     'BACKEND':'django.template.backends.jinja2.Jinja2',
    #     'DIRS': [os.path.join(BASE_DIR, 'templates')],
    #     'APP_DIRS': True,
    #     'OPTIONS':{
    #         'environment':'avicrypto.jinja2.environment'
    #     }
    # },
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

WSGI_APPLICATION = 'avicrypto.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ["avicrypto_db"],
        'USER': os.environ["avicrypto_user"],
        'PASSWORD': os.environ["avicrypto_pwd"],
        'HOST': os.environ["avicrypto_host"],
        'PORT': '5432'
    }
}

# using redis for caches
REDIS_URL = urlparse.urlparse(os.environ.get('REDIS_URL'))
CACHES = {
    "default": {
         "BACKEND": "redis_cache.RedisCache",
         "LOCATION": "{0}:{1}".format(REDIS_URL.hostname, REDIS_URL.port),
         "OPTIONS": {
             "PASSWORD": REDIS_URL.password,
             "DB": 0,
         }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# print BASE_DIR, PROJECT_PATH
# # STATIC_URL = '/static/'
# STATIC_URL = "https://178.62.252.134/avicrypto/staticfiles/"
# STATIC_ROOT = 'staticfiles'

# # STATICFILES_DIRS = (
# #     os.path.join(BASE_DIR, 'static'),
# # )
# STATIC_URL = '/static/'
# STATIC_URL = "https://codecakes.github.io/avi.github.io/staticfiles/"
# STATIC_ROOT = 'staticfiles'

# STATICFILES_DIRS = (
#     os.path.join(PROJECT_PATH, 'static'),
# )

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATIC_URL = '/static/'
STATIC_URL = "https://codecakes.github.io/avi.github.io/staticfiles/"

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder'
)

mailgun_conf = {
    'domain': 'avicrypto.us',
    'key': 'key-1055741f06d43a548bf5def6962b536a',
    'api': 'https://api.mailgun.net/v3/avicrypto.us/messages'
}
# django_heroku.settings(locals())



