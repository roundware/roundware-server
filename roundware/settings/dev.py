from .common import *

# Set Roundware API for internal calls to development environment
API_URL = "http://127.0.0.1:8888/roundware/"

# Change banned_timeout limit to better development testing value
BANNED_TIMEOUT_LIMIT = 90

# Remove possibility of demo stream to avoid confusion while testing
DEMO_STREAM_CPU_LIMIT = 0.0

INSTALLED_APPS += (
    # 'debug_toolbar',
)

DEBUG = True
for TEMPLATE_SETTINGS_BLOCK in TEMPLATES:
    TEMPLATE_SETTINGS_BLOCK['OPTIONS']['debug'] = DEBUG

DEBUG_TOOLBAR_PATCH_SETTINGS = False
CRISPY_FAIL_SILENTLY = not DEBUG



# MIDDLEWARE = (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ) + MIDDLEWARE


# Bypass the INTERNAL_IPS check for Debug Toolbar
class internal_list(list):

    def __contains__(self, key):
        return True
INTERNAL_IPS = internal_list()

# PROFILING using django-profiler
# PROFILING_SQL_QUERIES = True
LOGGING['handlers'] = {
    # The console handler will display in the manage.py runserver output
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'simple'
    },
    'file': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': '/var/log/roundware',
        'formatter': 'verbose',
    },
}

LOGGING['loggers'] = {
    # The default logger. Enable to log everything.
    # '': {
    #     'level': 'DEBUG',
    #     'handlers': ['console'],
    # },
    # The Django database logger. Enable to log all SQL queries.
    # 'django.db.backends': {
    #     'level': 'DEBUG',
    #     'handlers': ['console'],
    # },
    # The django-profiler logger. https://github.com/CodeScaleInc/django-profiler
    # 'profiling': {
    #     'level': 'DEBUG',
    #     'handlers': ['console'],
    # },
    # The roundware system logger.
    'roundware': {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    },
    # The Roundware API2 logger.
    # 'roundware.api2': {
    #     'level': 'DEBUG',
    #     'handlers': ['console'],
    # },
}

try:
    from .local_settings import *
except ImportError:
    pass
