import django
from django_coverage.settings import *
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
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}


if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
    TEST_DISCOVER_TOP_LEVEL = ROUNDWARE_SERVER_ROOT
    TEST_DISCOVER_ROOT = TEST_DISCOVER_TOP_LEVEL
    TEST_DISCOVER_PATTERN = 'test_*'
    COVERAGE_MODULE_EXCLUDES = ("roundware.rw.mommy_recipes",
                                "roundware.rw.templates", )
