from .common import *
try:
    from .local_settings import *
except ImportError:
    pass

# Set Roundware API for internal calls to development environment
API_URL = "http://127.0.0.1:8888/roundware/"

INSTALLED_APPS = INSTALLED_APPS + (
    'discoverage',
    'debug_toolbar',
)

DEBUG = True
TEMPLATE_DEBUG = True
DEBUG_TOOLBAR_PATCH_SETTINGS = False
CRISPY_FAIL_SILENTLY = not DEBUG

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES

# Bypass the INTERNAL_IPS check for Debug Toolbar
class internal_list(list):

    def __contains__(self, key):
        return True
INTERNAL_IPS = internal_list()

# PROFILING using django-profiler
PROFILING_SQL_QUERIES = True
LOGGING['handlers'].update({
    # The console handler will display in the manage.py runserver output
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose'
    },
})

LOGGING['loggers'].update({
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
    },
    # The roundwared stream manager logger.
    'roundwared': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    # The Roundware API2 logger.
    'api2': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    # Example logger for single file. Disable parent logger to use.
    # 'roundwared.stream': {
    #    'level': 'DEBUG',
    #    'handlers': ['console'],
    # },
})
