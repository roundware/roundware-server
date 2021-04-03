from .dev import *

LOGGING['handlers'] = {
    # The console handler will display in the manage.py runserver output
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'simple'
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

# Change banned_timeout limit to better testing value
BANNED_TIMEOUT_LIMIT = 3
