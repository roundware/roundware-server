from django import VERSION as django_version
from .dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    },
    'locmemcache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

# True when unit tests are running. Used by roundwared.recording_collection
TESTING = True

COVERAGE_OMIT_MODULES = ["roundware.rw.mommy_recipes",
                         "roundware.rw.templates", ]
