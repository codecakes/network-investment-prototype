# from avicrypto.local_settings import *
import os, urlparse

SECRET_KEY = 'q+@$$hpdjv$l-g9x7pz55_5#@fq29s@!25#r@_&$1_@l^j4-2z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# # Application definition

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
    'addons.wallet'
]
