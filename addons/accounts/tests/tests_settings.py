from avicrypto.local_settings import *
# import os, urlparse

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# # SECURITY WARNING: keep the secret key used in production secret!
# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# TEMPLATE_DEBUG = True

# # # Application definition

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
    'addons.wallet',
]
