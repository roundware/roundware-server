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

SOUTH_TESTS_MIGRATE = False

if django_version[:2] < (1, 6):
    from django_coverage.settings import *
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
    TEST_DISCOVER_TOP_LEVEL = ROUNDWARE_SERVER_ROOT
    TEST_DISCOVER_ROOT = TEST_DISCOVER_TOP_LEVEL
    TEST_DISCOVER_PATTERN = 'test_*'
    COVERAGE_MODULE_EXCLUDES = ("roundware.rw.mommy_recipes",
                                "roundware.rw.templates", )

COVERAGE_OMIT_MODULES = ["roundware.rw.mommy_recipes",
                         "roundware.rw.templates", ]
